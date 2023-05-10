import json
import networkx as nx
# from .src.config import *
import config as config
import matplotlib.pyplot as plt
import esprima
import pprint


class UnsupportTypeError(Exception):
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return f"Unsupport type: {self.type}"


class Call_graph:
    def __init__(self, js_file: str):
        # if js_file.endswith(".json"):
        #     with open(js_file, 'r', encoding='utf-8') as f:
        #         self.ast = json.load(f)
        # else:
        #     raise UnsupportTypeError
        self.ast = esprima.parse(js_file).toDict()
        # self.miniapp = miniapp
        # self.page = page
        self.now_in_func = [""]
        self.calling_relationship = {}
        self.js_call_graph = None
        self.funcs = []
        self.travel_ast(self.ast)

    def add_call_graph(self, value):
        # key = "->".join(map(str, now_in_func))
        key = self.now_in_func[-1]
        if key in self.calling_relationship:
            self.calling_relationship[key].append(value)
        else:
            self.calling_relationship[key] = [value]

    def do_travel_ast(self, visitor):
        # print(visitor)
        if (not isinstance(visitor, dict)) or ('type' not in visitor):
            return
        func_pointer = ["FunctionExpression", "ObjectExpression", "MemberExpression"]
        if visitor['type'] == "VariableDeclarator":
            if 'init' in visitor:
                    child = visitor['init']
                    if child is not None and 'type' in child and child['type'] in func_pointer:
                        id = self.travel_ast(visitor['id'])
                        self.now_in_func.append(id)
                        func = self.travel_ast(visitor['init'])
                        if func is not None:
                            self.add_call_graph(func)
                        self.now_in_func.pop()
                        return
            for key in visitor:
                self.travel_ast(visitor[key])
        elif visitor['type'] == "AssignmentExpression":
            if 'right' in visitor and visitor['right'] is not None and 'type' in visitor['right'] and visitor['right']['type'] in func_pointer:
                id = self.travel_ast(visitor['left'])
                self.now_in_func.append(id)
                func = self.travel_ast(visitor['right'])
                self.add_call_graph(func)
                self.now_in_func.pop()
                return 
            for key in visitor:
                self.travel_ast(visitor[key])
        elif visitor['type'] == "FunctionDeclaration":
            id = self.travel_ast(visitor['id'])
            self.funcs.append(id)
            self.now_in_func.append(id)
            for param in visitor['params']:
                self.travel_ast(param)
            self.travel_ast(visitor['body'])
            self.now_in_func.pop()
        elif visitor['type'] == "Property":
            key = self.travel_ast(visitor['key'])
            objection = self.now_in_func[-1]
            self.now_in_func.append(f"{objection}.{key}")
            self.travel_ast(visitor['value'])
            self.now_in_func.pop()
        # elif visitor['type'] == "ObjectExpression":
        # now_in_func.append(visitor[])
        elif visitor["type"] == "CallExpression":
            callee_func = self.travel_ast(visitor['callee'])
            self.funcs.append(callee_func)
            self.add_call_graph(callee_func)

            self.now_in_func.append(callee_func)
            for arg in visitor['arguments']:
                self.travel_ast(arg)
            self.now_in_func.pop()
            return callee_func

        elif visitor['type'] == "MemberExpression":
            object = self.travel_ast(visitor['object'])
            property = self.travel_ast(visitor['property'])
            return f"{object}.{property}"

        elif visitor['type'] == "Identifier":
            if 'name' not in visitor:
                return
            return visitor['name']
        else:
            for key in visitor:
                self.travel_ast(visitor[key])

    def travel_ast(self, visitor):
        if isinstance(visitor, dict):
            return self.do_travel_ast(visitor)
        elif isinstance(visitor, list):
            for item in visitor:
                self.do_travel_ast(item)
        else:
            return ""

    def construct_call_graph(self):
        if self.js_call_graph is None:
            self.js_call_graph = nx.DiGraph()
        for caller in self.calling_relationship:
            for callee in self.calling_relationship[caller]:
                if callee is not None:
                    # self.js_call_graph.add_edge(caller, callee, weight=1)
                    self.js_call_graph.add_edge(callee, caller, weight=1)

    def search_call_chain(self, target_func):
        if self.js_call_graph is None:
            self.construct_call_graph()
        if isinstance(target_func, str):
            target_func = [target_func]
        call_chains = {}
        for target in target_func:
            target_caller_funcs_length = {}
            target_caller_funcs = nx.descendants(self.js_call_graph, target)
            for caller in target_caller_funcs:
                try:
                    target_caller_funcs_length[caller] = len(nx.shortest_path(self.js_call_graph, target, caller))
                except nx.NetworkXNoPath:
                    pass
            sorted_target_caller_funcs = dict(sorted(target_caller_funcs_length.items(), key=lambda x: x[1]))
            call_chains[target] = list(sorted_target_caller_funcs.keys())
        return call_chains

    def draw_call_graph(self):
        if self.js_call_graph is None:
            self.construct_call_graph()
        save_path = '/root/minidroid'
        nx.nx_agraph.write_dot(self.js_call_graph, f"{save_path}/js_call_graph.dot")
        pos = nx.graphviz_layout(self.js_call_graph, prog='dot')
        nx.draw(self.js_call_graph, pos, with_labels=True, arrows=True)
        plt.savefig(f'{save_path}/js_call_graph.png')


if __name__ == '__main__':
    
    js_code = '''
function functionName(parameters) {
  // 函数体
  return result;
}
let person={data:functionName()}
let fuck = wx.fuck
fuck()
fuck = function() {}
a = wx.fuck

const name = 'Tom';
const age = 30;
const str = upper`My name is ${name} and I am ${age} years old.`;

function upper(strings, ...values) {
  let result = '';
  for (let i = 0; i < strings.length; i++) {
    result += strings[i];
    if (i < values.length) {
      result += String(values[i]).toUpperCase();
    }
  }
  return result;
}

var e = wx.getRecorderManager(),
	o = wx.createInnerAudioContext(),
	t = require("../../utils/formatDate.js"),
	a = getApp();
Page({
	data: {
		voices: [],
		flag: 0,
		playing: 0,
		tempFilePath: null,
		voicesLength: 0,
		visible2: !1,
		toggle: !1,
		actions2: [{
			name: "删除",
			color: "#ed3f14"
		}],
		navigateDetail: null
	},
	onHide: function() {},
	onUnload: function() {},
	onLoad: function(e) {
		var n = this;
		wx.cloud.callFunction({
				name: "login",
				data: {}
			})
			.then((function(e) {
				console.log("[云函数] [login] user openid: ", e.result.openid), n.setData({
					openid: e.result.openid
				});
				var o = e.result.openid;
				console.log(n.data.openid), wx.request({
					url: a.globalData.http_prefix + "/sys/audiorecord/list",
					data: {
						openid: o,
						limit: 1e3
					},
					header: {
						"content-type": "application/json"
					},
					success: function(e) {
						console.log("远程录音列表获取：", e);
						var o = e.data.page.list;
						console.log("onshow ==> res");
						for (var i = [], l = 0; l < o.length; l++) {
							console.log("时间："), console.log(o[l].createTime);
							var c = o[l].createTime,
								s = (o[l].size / 1024)
								.toFixed(2),
								r = l,
								d = {
									filePath: a.globalData.http_prefix + o[l].path,
									createTime: c,
									size: s,
									id: r,
									_id: o[l].id
								};
							i = i.concat(d)
						}
						var u, p = i.sort((u = "createTime", function(e, o) {
							var t = e[u],
								a = o[u];
							return t > a ? -1 : t < a ? 1 : 0
						}));
						for (l = 0; l < p.length; l++) {
							d = p[l], c = t.formatTime(new Date(d.createTime / 1e3 * 1e3));
							d.createTime = c
						}
						n.setData({
							voices: p,
							voicesLength: p.length
						}), console.log("[数据库] [查询记录] 成功: ", e)
					},
					fail: function(e) {
						wx.showToast({
							icon: "none",
							title: "查询记录失败"
						}), console.error("[数据库] [查询记录] 失败：", e)
					}
				})
			}))
			.catch((function(e) {
				console.error("[云函数] [login] 调用失败", e)
			})), o.onPlay((function() {
				console.log("开始播放"), n.setData({
					playing: 1
				})
			})), o.onStop((function() {
				console.log("i am onStop"), n.setData({
					playing: 0
				})
			})), o.onEnded((function() {
				console.log("i am onEnded"), n.setData({
					playing: 0
				})
			})), o.onError((function(e) {
				console.log(e.errMsg), console.log(e.errCode), n.setData({
					playing: 0
				})
			}))
	},
	onShow: function() {
		var e = null;
		wx.createInterstitialAd && ((e = wx.createInterstitialAd({
					adUnitId: "adunit-160b2120c1223204"
				}))
				.onLoad((function() {})), e.onError((function(e) {})), e.onClose((function() {}))), e && e.show()
			.catch((function(e) {
				console.error(e)
			}));
		var o = this;
		wx.request({
			url: "https://zz.niuit.top/control/sys/applet/single",
			data: {
				param: "cloudRecord_index"
			},
			header: {
				"content-type": "application/json"
			},
			success: function(e) {
				o.setData({
					navigateDetail: e.data
				})
			}
		})
	},
	getRemoteRecordList: function(e) {
		wx.request({
			url: a.globalData.http_prefix + "/sys/audiorecord/list",
			data: {
				openid: e,
				limit: 1e3
			},
			header: {
				"content-type": "application/json"
			},
			success: function(e) {
				console.log("远程录音列表获取：", e), fileList = e.data.page.list
			}
		})
	},
	_del: function(e) {
		var o = this.data.openid;
		console.log(o), console.log(e);
		var t = e.currentTarget.dataset.id;
		wx.showModal({
			title: "提示",
			content: "确定要删除吗",
			success: function(e) {
				e.confirm ? (console.log("用户点击确定"), wx.request({
					url: a.globalData.http_prefix + "/sys/audiorecord/delete/single",
					data: {
						id: t,
						openid: o
					},
					header: {
						"content-type": "application/json"
					},
					success: function(e) {
						console.log("删除远程录音：", e)
					}
				})) : e.cancel && console.log("用户点击取消")
			}
		})
	},
	startRecord: function() {
		var o = null;
		wx.createInterstitialAd && ((o = wx.createInterstitialAd({
				adUnitId: "adunit-160b2120c1223204"
			}))
			.onLoad((function() {})), o.onError((function(e) {})), o.onClose((function() {}))), console.log("startRecord...");
		this.setData({
			flag: 1
		}), wx.showToast({
			title: "开始录音",
			icon: "success",
			duration: 1e3
		});
		e.start({
			duration: 6e5,
			sampleRate: 16e3,
			numberOfChannels: 1,
			encodeBitRate: 96e3,
			format: "mp3",
			frameSize: 50
		}), e.onStart((function() {
			console.log("recorder start")
		})), e.onError((function(e) {
			console.log(e)
		}))
	},
	gotoPlay: function(e) {
		var t = null;
		wx.createInterstitialAd && ((t = wx.createInterstitialAd({
				adUnitId: "adunit-160b2120c1223204"
			}))
			.onLoad((function() {})), t.onError((function(e) {})), t.onClose((function() {}))), console.log(e);
		var a = e.currentTarget.dataset.key;
		wx.setInnerAudioOption({
			mixWithOther: !1,
			obeyMuteSwitch: !1
		}), o.autoplay = !0, o.src == a ? (console.log("开始播放play"), o.play()) : (o.src = a, console.log("开始播放onCanplay"), o.onCanplay((function() {
			o.play()
		})))
	},
	endRecord: function() {
		var o = this,
			t = null;
		wx.createInterstitialAd && ((t = wx.createInterstitialAd({
				adUnitId: "adunit-160b2120c1223204"
			}))
			.onLoad((function() {})), t.onError((function(e) {})), t.onClose((function() {}))), console.log("endRecord...");
		var n = this;
		e.stop(), e.onStop((function(e) {
			o.tempFilePath = e.tempFilePath, console.log("停止录音", e);
			e.tempFilePath;
			o.setData({
				record: e.tempFilePath,
				size: e.fileSize
			});
			var t = o.data.record;
			console.log(t), console.log(t.substr(t.lastIndexOf("_") + 1)), wx.uploadFile({
				url: a.globalData.http_prefix + "/sys/file/upload",
				filePath: t,
				formData: {
					openid: n.data.openid
				},
				name: "file",
				success: function(e) {
					console.log("录音文件地址", e);
					var o = JSON.parse(e.data),
						t = o.data.filePath,
						i = o.data.fileName;
					n.setData({
						fileUrl: o.data
					}), a.globalData.filePath = t, console.log(a.globalData.filePath);
					var l = Date.parse(new Date);
					console.log("当前时间戳为：" + l), wx.request({
						url: a.globalData.http_prefix + "/sys/audiorecord/save",
						method: "POST",
						data: {
							openid: n.data.openid,
							creator: "niu",
							record: t,
							path: "/audio/" + n.data.openid + "/" + i,
							createTime: l,
							size: n.data.size,
							status: 0
						},
						header: {
							"content-type": "application/json"
						},
						success: function(e) {
							console.log("上传录音返回：", e), n.setData({
								recordId: e.id
							}), n.setData({
								flag: 0
							}), wx.showToast({
								title: "新增记录成功"
							})
						},
						fail: function(e) {
							wx.showToast({
								icon: "none",
								title: "新增记录失败"
							}), console.error("[数据库] [新增记录] 失败：", e)
						}
					})
				},
				fail: function(e) {
					console.error("[上传文件] 失败：", e), wx.showToast({
						icon: "none",
						title: "上传失败"
					})
				},
				complete: function() {
					o.setData({
						flag: 0
					}), wx.hideLoading(), n.getRecordList(n.data.openid, n)
				}
			})
		}))
	},
	videoAd: function() {
		var e = null;
		wx.createRewardedVideoAd && (e = wx.createRewardedVideoAd({
				adUnitId: "adunit-87b712969e247068"
			}), e.onLoad((function() {})), e.onError((function(e) {})), e.onClose((function(e) {}))), e && e.show()
			.catch((function() {
				e.load()
					.then((function() {
						return e.show()
					}))
					.catch((function(e) {
						console.log("激励视频 广告显示失败")
					}))
			}))
	},
	onShareAppMessage: function(e) {
		console.log("分享"), console.log(e), this.videoAd();
		var o = e.target.dataset.voice;
		return console.log(o), null != o ? {
			title: "录音器",
			desc: "实时录音,永久存储",
			path: "pages/other/other?filePath=" + o.filePath + "&createTime=" + o.createTime + "&size=" + o.size
		} : {
			title: "录音器",
			desc: "实时录音,永久存储",
			path: "pages/welcome/welcome"
		}
	},
	shareVioce: function(e) {
		var o = e.currentTarget.dataset.voice;
		console.log(o), this.onShareAppMessage(o)
	},
	music: function() {
		console.log("navigateDetail ", this.data.navigateDetail);
		var e = this.data.navigateDetail;
		null == e ? wx.request({
			url: "https://zz.niuit.top/control/sys/applet/single",
			data: {
				param: "cloudRecord_index"
			},
			header: {
				"content-type": "application/json"
			},
			success: function(e) {
				wx.navigateToMiniProgram({
					appId: e.data.data.appKey,
					path: e.data.data.appPath,
					extraData: {},
					envVersion: "release",
					success: function(e) {
						console.log(e)
					}
				})
			}
		}) : wx.navigateToMiniProgram({
			appId: e.data.appKey,
			path: e.data.appPath,
			extraData: {},
			envVersion: "release",
			success: function(e) {
				console.log(e)
			}
		})
	},
	getRecordList: function(e, o) {
		console.log(o.data.openid);
		var n = o;
		wx.request({
			url: a.globalData.http_prefix + "/sys/audiorecord/list",
			data: {
				openid: e,
				limit: 1e3
			},
			header: {
				"content-type": "application/json"
			},
			success: function(e) {
				console.log("远程录音列表获取：", e);
				var o = e.data.page.list;
				console.log("onshow ==> res");
				for (var i = [], l = 0; l < o.length; l++) {
					console.log("时间："), console.log(o[l].createTime);
					var c = o[l].createTime,
						s = (o[l].size / 1024)
						.toFixed(2),
						r = l,
						d = {
							filePath: a.globalData.http_prefix + o[l].path,
							createTime: c,
							size: s,
							id: r,
							_id: o[l].id
						};
					i = i.concat(d)
				}
				var u, p = i.sort((u = "createTime", function(e, o) {
					var t = e[u],
						a = o[u];
					return t > a ? -1 : t < a ? 1 : 0
				}));
				for (l = 0; l < p.length; l++) {
					d = p[l], c = t.formatTime(new Date(d.createTime / 1e3 * 1e3));
					d.createTime = c
				}
				n.setData({
					voices: p,
					voicesLength: p.length
				}), console.log("[数据库] [查询记录] 成功: ", e)
			},
			fail: function(e) {
				wx.showToast({
					icon: "none",
					title: "查询记录失败"
				}), console.error("[数据库] [查询记录] 失败：", e)
			}
		})
	}
});
    '''
    print(nx.__version__)
    ast_analyzer = Call_graph(js_code)
    # pprint.pprint(ast_analyzer.search_call_chain("wx.request"))
    ast_analyzer.draw_call_graph()
