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

import graphviz
import pydotplus
from collections import defaultdict
from loguru import logger
import config as config
from typing import List
from miniapp import MiniApp, Page, Navigator, NavigateAPI
from bs4 import Tag
from pdg_js.js_operators import get_node_computed_value


class Node():
    node_dict = {}

    # TODO: 该构造方法的生存周期？
    # 在节点类的构造方法 __new__ 中，先在 node_dict 中查找是否存在同名节点实例，如果存在，则直接返回该实例；
    # 否则，再调用 super().__new__(cls) 方法创建新的节点实例并返回
    def __new__(cls, name):
        if name in cls.node_dict:
            return cls.node_dict[name]
        else:
            return super().__new__(cls)

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children: List[Node] = []
        Node.node_dict[name] = self
    
    def add_child(self, child: 'Node'):
        self.children.append(child)
        child.parent = self

    @classmethod
    def get_node_by_name(cls, name):
        return cls.node_dict.get(name)

class FuncNode(Node):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def set_trigger_tag(self, tag: Tag):
        self.trigger_tag = tag

    def set_sensi_api(self, sensi_api: str):
        # TODO: sensi_api is instance of CallExpression
        self.sensi_api = sensi_api


class PageNode(Node):
    def __init__(self, name, parent, page: Page, beacon):
        super().__init__(name, parent)
        self.page = page
        self.set_beacon(beacon)
    
    def set_beacon(self, beacon: Navigator or NavigateAPI):
        self.beacon = beacon


# TODO: 基于Node对FCG、UTG、MDG进行重构
class UTG():
    def __init__(self, miniapp: MiniApp):
        self.miniapp = miniapp
        self.utg = Node(name=self.miniapp.name, parent=None)
        self.produce_utg()

    def produce_utg(self):
        # add tabBar PageNode
        for tabBar in self.miniapp.tabBars.keys():
            self.utg.add_child(PageNode(name=tabBar, parent=self.utg, 
                                page=self.miniapp.tabBars[tabBar], beacon=None))
        # add navigator PageNode
        for page in self.miniapp.pages.keys():
            for navigator in self.miniapp.pages[page].navigator['UIElement']:
                if navigator.target == 'self':
                    if Node.get_node_by_name(page) is not None:
                        pass

            


    def produce_utgviz(self, graph=graphviz.Digraph(comment='UI Transition Graph',
                                                 graph_attr={"concentrate": "true", "splines": "false"})):
        page_node_style = ['box', 'red', 'lightpink']
        graph.attr('node', shape=page_node_style[0], style='filled',
                   color=page_node_style[2], fillcolor=page_node_style[2])
        graph.attr('edge', color=page_node_style[1])
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
            if "label" in edge.get_attributes().keys():
                label = edge.get_attributes()["label"]
            else:
                label = None
            utg[src].append((dst, label))
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
                graph.attr('node', style='filled', color='lightgoldenrodyellow',
                           fillcolor='lightgoldenrodyellow')
                graph.attr('edge', color='orange')
                graph.edge(func, callee)
                func_node_style = ['ellipse', 'goldenrod1', 'goldenrod1']
                graph.attr('node', shape=func_node_style[0], style='filled', color=func_node_style[2],
                           fillcolor=func_node_style[2])
                graph.attr('edge', color=func_node_style[1])
            else:
                graph.edge(func, callee)
            if callee in call_graph.keys():
                graph = self.add_callee_edge_to_graph(graph, call_graph, func=callee)
        return graph

    def produce_fcgviz(self, graph=graphviz.Digraph(graph_attr={"concentrate": "true", "splines": "false"},
                                                 comment='Function Call Graph')):
        page_node_style = ['box', 'red', 'lightpink']
        graph.attr('node', shape=page_node_style[0], style='filled',
                   color=page_node_style[2], fillcolor=page_node_style[2])
        graph.node(name=self.page.page_path)
        func_node_style = ['ellipse', 'goldenrod1', 'goldenrod1']
        graph.attr('node', shape=func_node_style[0], style='filled', color=func_node_style[2],
                   fillcolor=func_node_style[2])
        graph.attr('edge', color=func_node_style[1])
        # graph.edge(self.page.page_path, 'BindingEvent')
        # graph.edge(self.page.page_path, 'LifecycleCallback')
        # BindingEvent Call Graph
        for binding in self.page.binding_event.keys():
            if len(self.page.binding_event[binding]):
                for event in self.page.binding_event[binding]:
                    # event_contents=' '
                    # event_contents.join(event.contents)
                    graph.edge(self.page.page_path, event.handler, label=event.trigger)
                    func = event.handler
                    call_graph = self.get_all_callee_from_func(func, call_graph={})
                    if call_graph is not None:
                        if func in call_graph.keys():
                            graph = self.add_callee_edge_to_graph(graph, call_graph, func)

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
            if "label" in edge.get_attributes().keys():
                label = edge.get_attributes()["label"]
            else:
                label = None
            fcg[src].append((dst, label))
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
        page_node_style = ['box', 'red', 'lightpink']
        graph.attr('node', shape=page_node_style[0], style='filled',
                   color=page_node_style[2], fillcolor=page_node_style[2])
        graph.attr('edge', color=page_node_style[1])
        for tabBar in self.miniapp.tabBars.keys():
            graph.edge('MiniApp', str(tabBar))
        for page in self.miniapp.pages.keys():
            page_node_style = ['box', 'red', 'lightpink']
            graph.attr('node', shape=page_node_style[0], style='filled', color=page_node_style[2],
                       fillcolor=page_node_style[2])
            graph.attr('edge', color=page_node_style[1])
            for navigator in self.miniapp.pages[page].navigator['UIElement']:
                if navigator.target == 'self':
                    graph.edge(str(page), str(navigator.url), label=navigator.type)
            for navigator in self.miniapp.pages[page].navigator['NavigateAPI']:
                if navigator.name in ('wx.navigateTo', 'wx.navigateBack'):
                    graph.edge(str(page), str(navigator.target), label=navigator.name)
            graph = self.miniapp.pages[page].produce_fcg(graph=graph)
        return graph