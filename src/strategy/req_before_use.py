from loguru import logger
from miniapp import MiniApp
from pdg_js.js_operators import get_node_computed_value
import config as config


def check_req_before_use(miniapp: MiniApp):
    """
        Check if Request Permission before Use.

        -------
        Parameters:
        - miniapp: MiniApp =>
            Instance of the miniapp to be detected

        -------
        Return:
        - result/None: dict =>
            result = {
                'authorize_scope': authorize_scopes,
                'sensi_apis': sensi_apis,
                'violation_pages': violation_page
            }
        - authorize_scopes: set =>
            A list of privacy scopes authorization before using miniapp
        - sensi_apis: set =>
            A list of sensitive api call before using miniapp
        - violation_pages: set =>
            app.js/index.js
    """
    authorize_scopes = set()
    sensi_apis = set()
    violation_pages = set()
    # Check miniapp init behavior
    app_method_nodes = miniapp.app_method_nodes
    for method_name in app_method_nodes.keys():
        if method_name in ('onLaunch', 'onShow'):
            authorize_scopes, sensi_apis = violation_checker(app_method_nodes[method_name],
                                                             authorize_scopes, sensi_apis)
            violation_pages.add('app.js')
            # if len(authorize_scopes) or len(sensi_apis):
            #     logger.info('''[req_before_use] Violation Detected in {}. [authorize_scopes] {} [sensi_apis] {}''' \
            #                 .format(miniapp.miniapp_path+'/app.js', authorize_scopes, sensi_apis))

    # Check index page init behavior
    page = miniapp.pages[miniapp.index_page]
    page_method_nodes = page.page_method_nodes
    for method_name in page_method_nodes.keys():
        if method_name in ('onLoad', 'onShow', 'onReady'):
            authorize_scopes, sensi_apis = violation_checker(page_method_nodes[method_name],
                                                             authorize_scopes, sensi_apis)
            violation_pages.add(page.page_path)
            # if len(authorize_scopes) or len(sensi_apis):
            #     logger.info('''[req_before_use] Violation Detected in {}. [authorize_scopes] {} [sensi_apis] {}''' \
            #                 .format(miniapp.name+page.page_path, authorize_scopes, sensi_apis))

    # Return result
    if len(authorize_scopes) or len(sensi_apis):
        result = {
            'authorize_scope': list(authorize_scopes),
            'sensi_apis': list(sensi_apis),
            'violation_page': list(violation_pages)
        }
        return result
    else:
        return None


def violation_checker(method_node, authorize_scopes: set, sensi_apis: set):
    for child in method_node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value(callee)
                if call_expr_value == 'wx.authorize':
                    authorize_scopes = get_authorize_scopes(child, authorize_scopes=authorize_scopes)
                elif call_expr_value in config.SENSITIVE_API.keys():
                    sensi_apis.add(call_expr_value)
        authorize_scopes, sensi_apis = violation_checker(child, authorize_scopes, sensi_apis)
    return authorize_scopes, sensi_apis


def get_authorize_scopes(child, authorize_scopes: set):
    obj_exp = child.children[1]
    for prop in obj_exp.children:
        if get_node_computed_value(prop.children[0]) == 'scope':
            scope = get_node_computed_value(prop.children[1])
            if scope in config.SENSITIVE_API.keys():
                authorize_scopes.add(scope)
    return authorize_scopes
