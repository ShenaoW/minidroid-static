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


class UTG():
    def __init__(self, miniapp: MiniApp):
        self.miniapp = miniapp
        self.page_navigators = {}
        self.utg = self.produce_utg()

    def produce_utg(self, graph=graphviz.Digraph(comment='UI Transition Graph',
                                                 graph_attr={"concentrate": "true", "splines": "false"})):
        for tabBar in self.miniapp.tabBars.keys():
            graph.edge('MiniApp', str(tabBar))
        for page in self.miniapp.pages.keys():
            for navigator in self.miniapp.pages[page].navigator['UIElement']:
                if navigator.target == 'self':
                    graph.edge(str(page), str(navigator.url))
                    self.page_navigators[(str(page), str(navigator.url))] = navigator
            for navigator in self.miniapp.pages[page].navigator['NavigateAPI']:
                if navigator.name in ('wx.navigateTo', 'wx.navigateBack'):
                    graph.edge(str(page), str(navigator.target))
                    self.page_navigators[(str(page), str(navigator.target))] = navigator
        return graph

    def get_utg_dict(self):
        utg = defaultdict(list)
        dot = self.utg.source
        graph = pydotplus.graph_from_dot_data(data=dot)
        for edge in graph.get_edges():
            src, dst = edge.get_source().strip('"'), edge.get_destination().strip('"')
            utg[src].append(dst)
        return dict(utg)

    def draw_utg(self, save_path=config.SAVE_PATH_UTG):
        save_path += '/' + self.miniapp.name + '/' + self.miniapp.name
        dot = self.utg
        if save_path is None:
            dot.view()
        else:
            dot.render(save_path, view=False)
            graphviz.render(filepath=save_path, engine='dot', format='eps')
        dot.clear()


class FCG():
    def __init__(self, page: Page):
        self.page = page
        self.trigger_event = {}
        self.reachable_sensi_api_paths = {}
        self.fcg = self.produce_fcg()

    def produce_fcg(self, graph=graphviz.Digraph(graph_attr={"concentrate": "true", "splines": "false"},
                                                 comment='Function Call Graph')):
        graph.node(name=self.page.page_path)
        # BindingEvent Call Graph
        for binding in self.page.binding_event.keys():
            if len(self.page.binding_event[binding]):
                for event in self.page.binding_event[binding]:
                    graph.edge(self.page.page_path, event.handler)
                    func = event.handler
                    self.trigger_event[func] = event
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
                    if isinstance(call_expr_value, str):
                        if call_expr_value in self.page.page_method_nodes.keys():
                            if call_graph.get(func, False):
                                # avoid self-calling/recursive calling loops
                                if call_expr_value != func and call_expr_value not in call_graph[func]:
                                    call_graph[func].add(call_expr_value)
                                    self.get_all_callee_from_func(call_expr_value, call_graph)
                            else:
                                call_graph[func] = set()
                                call_graph[func].add(call_expr_value)
                                self.get_all_callee_from_func(call_expr_value, call_graph)
                        elif call_expr_value in config.SENSITIVE_API:
                            call_graph[func] = set()
                            call_graph[func].add(call_expr_value)
            call_graph = self.traverse_children_to_build_func_call_chain(func, child, call_graph)
        return call_graph

    def add_callee_edge_to_graph(self, graph, call_graph, func):
        for callee in call_graph[func]:
            if callee in config.SENSITIVE_API:
                graph.edge(func, callee)
            elif callee in call_graph.keys():
                graph.edge(func, callee)
                if callee not in call_graph[callee]:  # avoid self-calling loops
                    if func not in call_graph[callee]:  # avoid recursive calling loops
                        graph = self.add_callee_edge_to_graph(graph, call_graph, func=callee)
        return graph

    def get_fcg_dict(self):
        fcg = defaultdict(list)
        dot = self.fcg.source
        graph = pydotplus.graph_from_dot_data(data=dot)
        for edge in graph.get_edges():
            src, dst = edge.get_source().strip('"'), edge.get_destination().strip('"')
            fcg[src].append(dst)
        return dict(fcg)

    def draw_fcg(self, save_path=config.SAVE_PATH_FCG):
        save_path += '/' + self.page.miniapp.name + '/' + self.page.page_path
        dot = self.fcg
        if save_path is None:
            dot.view()
        else:
            dot.render(save_path, view=False)
            graphviz.render(filepath=save_path, engine='dot', format='eps')
        dot.clear()

    def get_sensi_api_trigger_path(self, sensi_api):
        pass


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
    miniapp = MiniApp('/root/minidroid/dataset/miniprograms/wx78aede17802a14ab')
    utg = UTG(miniapp)
    utg.draw_utg()
    for page in miniapp.pages.values():
        fcg = FCG(page)
        print('[Success]{}'.format(page.page_path))
        fcg.draw_fcg()