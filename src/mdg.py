# coding: utf8

"""
    Definition of Class
    - Node
    - FuncNode
    - PageNode
    - UTG(miniapp)
    - FCG(page)
    - MDG(miniapp)
"""

import pprint
import graphviz
import pydotplus
from collections import defaultdict
from loguru import logger
import config as config
from miniapp import MiniApp, Page
from bs4 import Tag
from pdg_js.js_operators import get_node_computed_value


# TODO: 基于Node对FCG、UTG、MDG进行重构(如何解决多个parent路径对应的问题)
class UTG():
    def __init__(self, miniapp: MiniApp):
        self.miniapp = miniapp
        self.trigger = {}

    def produce_utgviz(self, graph=graphviz.Digraph(comment='UI Transition Graph',
                                                 graph_attr={"concentrate": "true", "splines": "false"})):
        for tabBar in self.miniapp.tabBars.keys():
            graph.edge('MiniApp', str(tabBar))
        for page in self.miniapp.pages.keys():
            for navigator in self.miniapp.pages[page].navigator['UIElement']:
                if navigator.target == 'self':
                    graph.edge(str(page), str(navigator.url))
            for navigator in self.miniapp.pages[page].navigator['NavigateAPI']:
                if navigator.name in ('wx.navigateTo', 'wx.navigateBack'):
                    graph.edge(str(page), str(navigator.target))
        return graph

    def get_utg_dict(self):
        utg = defaultdict(list)
        dot = self.produce_utgviz().source
        graph = pydotplus.graph_from_dot_data(data=dot)
        for edge in graph.get_edges():
            src, dst = edge.get_source().strip('"'), edge.get_destination().strip('"')
            utg[src].append(dst)
        return dict(utg)

    def draw_utg(self, save_path=config.SAVE_PATH_UTG):
        save_path += '/' + self.miniapp.name + '/' + self.miniapp.name
        dot = self.produce_utgviz()
        if save_path is None:
            dot.view()
        else:
            dot.render(save_path, view=False)
            graphviz.render(filepath=save_path, engine='dot', format='eps')
        dot.clear()


class FCG():
    def __init__(self, page: Page):
        self.page = page
    
    def get_all_callee_from_func(self, func: str, call_graph):
        try:
            func_node = self.page.page_method_nodes[func]
        except:
            logger.warning("FuncNotFoundError: function {} in {} not found!".format(func, self.page.page_path))
            return None
        call_graph = self.traverse_children_to_build_func_call_chain(func, func_node, call_graph)
        return call_graph

    def traverse_children_to_build_func_call_chain(self, func: str, node, call_graph):
        for child in node.children:
            if child.name in ('CallExpression', 'TaggedTemplateExpression'):
                if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                    if child.children[0].name == 'MemberExpression' \
                            and child.children[0].children[0].name == 'ThisExpression':
                        callee = child.children[0].children[1]
                    else:
                        callee = child.children[0]
                    call_expr_value = get_node_computed_value(callee)
                    if call_expr_value in self.page.page_method_nodes.keys():
                        if call_graph.get(func, False):
                            call_graph[func].append(call_expr_value)
                        else:
                            call_graph[func] = [call_expr_value]
                        self.get_all_callee_from_func(call_expr_value, call_graph)
                    elif call_expr_value in config.SENSITIVE_API:
                        call_graph[func] = [call_expr_value]
            call_graph = self.traverse_children_to_build_func_call_chain(func, child, call_graph)
        return call_graph

    def add_callee_edge_to_graph(self, graph, call_graph, func):
        for callee in call_graph[func]:
            if callee in config.SENSITIVE_API:
                graph.edge(func, callee)
            else:
                graph.edge(func, callee)
            if callee in call_graph.keys():
                graph = self.add_callee_edge_to_graph(graph, call_graph, func=callee)
        return graph

    def produce_fcgviz(self, graph=graphviz.Digraph(graph_attr={"concentrate": "true", "splines": "false"},
                                                 comment='Function Call Graph')):
        graph.node(name=self.page.page_path)
        # BindingEvent Call Graph
        for binding in self.page.binding_event.keys():
            if len(self.page.binding_event[binding]):
                for event in self.page.binding_event[binding]:
                    graph.edge(self.page.page_path, event.handler)
                    func = event.handler
                    call_graph = self.get_all_callee_from_func(func, call_graph={})
                    if call_graph is not None:
                        if func in call_graph.keys():
                            graph = self.add_callee_edge_to_graph(graph, call_graph, func)
        # LifecycleEvent Call Graph
        for func in self.page.page_method_nodes.keys():
            if func in ('onLoad', 'onShow', 'onReady', 'onHide', 'onUnload'):
                graph.edge(self.page.page_path, func)
                call_graph = self.get_all_callee_from_func(func, call_graph={})
                if call_graph is not None:
                    if func in call_graph.keys():
                        graph = self.add_callee_edge_to_graph(graph, call_graph, func)
        return graph

    def get_fcg_dict(self):
        fcg = defaultdict(list)
        dot = self.produce_fcgviz().source
        graph = pydotplus.graph_from_dot_data(data=dot)
        for edge in graph.get_edges():
            src, dst = edge.get_source().strip('"'), edge.get_destination().strip('"')
            # if "label" in edge.get_attributes().keys():
            #     label = edge.get_attributes()["label"]
            # else:
            #     label = None
            fcg[src].append(dst)
        return dict(fcg)

    def draw_fcg(self, save_path=config.SAVE_PATH_FCG):
        save_path += '/' + self.page.miniapp.name + '/' + self.page.page_path
        dot = self.produce_fcgviz()
        if save_path is None:
            dot.view()
        else:
            dot.render(save_path, view=False)
            graphviz.render(filepath=save_path, engine='dot', format='eps')
        dot.clear()


class MDG():
    def __init__(self, miniapp: MiniApp):
        self.miniapp = miniapp
    
    def produce_mdgviz(self, graph=graphviz.Digraph(comment='MiniApp Dependency Graph',
                                                 graph_attr={"concentrate": "true", "splines": "false"})):
        for tabBar in self.miniapp.tabBars.keys():
            graph.edge('MiniApp', str(tabBar))
        for page in self.miniapp.pages.keys():
            for navigator in self.miniapp.pages[page].navigator['UIElement']:
                if navigator.target == 'self':
                    graph.edge(str(page), str(navigator.url), label=navigator.type)
            for navigator in self.miniapp.pages[page].navigator['NavigateAPI']:
                if navigator.name in ('wx.navigateTo', 'wx.navigateBack'):
                    graph.edge(str(page), str(navigator.target), label=navigator.name)
            graph = self.miniapp.pages[page].produce_fcg(graph=graph)
        return graph
    

if __name__ == '__main__':
    miniapp = MiniApp('/root/minidroid/dataset/miniprogram-demo')
    # utg = UTG(miniapp)
    # pprint.pprint(utg.get_utg_dict())
    for page in miniapp.pages.values():
        fcg = FCG(page)
        pprint.pprint(fcg.get_fcg_dict())
        break
