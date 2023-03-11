import os
from miniapp import MiniApp
from pdg_js.js_operators import get_node_computed_value
import config as config


def check_compulsory_reqs(miniapp: MiniApp):
    '''
        Check if Request Permission Compulsory

        -------
        Parameters:
        - miniapp: MiniApp =>
             Instance of the miniapp to be detected
        
        -------
        Return:
        - violations/None: list(dict) =>
            A list of violation{
                'page': page.page_path,
                'navigateToSuspiciousPage': False/True,
                'showSuspiciousModel': False/OptionalCase
            }
    '''
    violations = []
    for page in miniapp.pages.values():
        violation = {
            'page': page.page_path,
            'navigateToSuspiciousPage': False,
            'showSuspiciousModel': False  # default False, optional=('cancelToExit', 'compulsoryOpenSetting')
        }
        violation = violation_checker(page.pdg_node, page, violation)
        if violation['navigateToSuspiciousPage'] or violation['showSuspiciousModel']:
            violations.append(violation)
    if len(violations):
        return violations
    else: return None

def violation_checker(node, page, violation):
    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if type(call_expr_value) == 'str':
                    if call_expr_value == 'wx.authorize' or call_expr_value in config.SENSITIVE_API:
                        violation = check_fail_callback(child, page, violation)
        violation = violation_checker(child, page, violation)
    return violation

def check_fail_callback(node, page, violation):
    if len(node.children)==2:
        obj_exp = node.children[1]
        for prop in obj_exp.children:
            if get_node_computed_value(prop.children[0]) == 'fail':
                url = check_if_navigate(prop)
                if url != None:
                    violation['navigateToSuspiciousPage'] = check_if_navigate_page_suspicious(page, url)
                violation['showSuspiciousModel'] = check_if_showmodel_suspicious(page, prop)
    return violation

def check_if_navigate(node):
    url = None
    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
           if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if type(call_expr_value) == 'str':
                    if call_expr_value == 'wx.navigateTo':
                        obj_exp = child.children[1]
                        for prop in obj_exp.children:
                            if get_node_computed_value(prop.children[0]) == 'url':
                                url = get_node_computed_value(prop.children[1])
                                return url
        url = check_if_navigate(child)
    return url

def check_if_navigate_page_suspicious(page, url):
    target = os.path.join(page.miniapp.miniapp_path, url)
    result = check_target_page(page.miniapp.pages[target])
    return result

def check_target_page(page):
    for child in page.pdg_node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if call_expr_value == 'wx.openSetting':
                    return True
    return False

def check_if_showmodel_suspicious(page, node):
    showSuspiciousModel = False
    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
           # 不止要检查wx.showModal直接调用, 也要对page method间接调用wx.showModal做检查
           if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if type(call_expr_value) == 'str':
                    # Check direct API(wx.showMedel) call
                    if call_expr_value == 'wx.showModal':
                        obj_exp = child.children[1]
                        showCancel_value = True
                        for prop in obj_exp.children:
                            if get_node_computed_value(prop.children[0]) == 'showCancel':
                                showCancel_value = get_node_computed_value(prop.children[1])
                            # 不管success/fail/complete回调都做检查，并且对于success回调中的if逻辑不做特殊处理
                            # 只要异步回调中有授权调用或者退出调用，都视为违规case
                            if get_node_computed_value(prop.children[0]) in ('success', 'fail', 'complete'):
                                result = check_asyn_func_expr(prop.children[1], result=[])
                                if showCancel_value == False and 'openSetting' in result:
                                    showSuspiciousModel = 'compulsoryOpenSetting'
                                    return showSuspiciousModel
                                elif 'cancelToExit' in result:
                                    showSuspiciousModel = 'cancelToExit'
                                    return showSuspiciousModel
                    # Check indirect API(wx.showModal) call
                    elif call_expr_value in page.page_method_nodes.keys():
                        showSuspiciousModel = check_if_showmodel_suspicious(page, page.page_method_nodes[call_expr_value])
        showSuspiciousModel = check_if_showmodel_suspicious(page, child)
    return showSuspiciousModel

def check_asyn_func_expr(node, result):
    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if type(call_expr_value) == 'str':
                    if call_expr_value == 'wx.openSetting':
                        result.append('openSetting')
                    elif call_expr_value == 'wx.exitMiniProgram':
                        result.append('cancelToExit')
        result = check_asyn_func_expr(child, result) 
    return result
