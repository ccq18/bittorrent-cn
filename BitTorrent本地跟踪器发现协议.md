BitTorrent本地跟踪器发现协议 
http://www.bittorrent.org/beps/bep_0022.html

 
## 动机

一些Internet服务提供商（ISP）可能希望对流量进行本地化以降低传输成本，减少内部流量并通过加快下载速度来改善用户体验。

通过此扩展，BitTorrent客户端能够发现网络上附近的跟踪器，并通过该跟踪器发现附近的缓存或对等点。缓存可能只是网络中间的快速对等点。它还可能具有大量的磁盘空间。客户端使用普通的BitTorrent协议与缓存进行通信。

当存在高速缓存时，用户将受益于拥有高容量的对等方，用户的客户端可以从该对等方下载并且可以委托其播种。当用户的ISP网络内部的缓存代表客户端播种时，它释放了用户访问网络中的上游容量，使用户和共享访问网络的用户受益。当后续的对等方从其ISP的缓存中传输时，ISP的传输流量将减少。

该BEP的范围仅限于本地跟踪器发现过程。BitTorrent协议套件的扩展以委托种子或提高缓存性能超出了本BEP的范围。

本文档中的关键字“必须”，“不得”，“必须”，“应”，“应禁止”，“应”，“不应”，“建议”，“可以”和“可选”是如IETF RFC 2119 [[5]中](http://www.bittorrent.org/beps/bep_0022.html#rfc-2119)所述进行解释。

客户端实施本地跟踪器发现是可选的。客户不得向本地跟踪器发布私人种子。建议客户端提供用于关闭本地跟踪器发现的用户选项。默认情况下，本地跟踪器发现可能处于关闭状态。如果性能优势不明显，客户端可以自动关闭缓存。确定明显性超出了本BEP的范围。

## 发现机制

为了找到其ISP的跟踪器，BitTorrent客户端对其外部IP地址执行反向DNS查找，然后获取与主机域名关联的BitTorrent SRV资源记录。例如，地址为69.107.0.14的主机在以下位置获取PTR记录

14.0.107.69.in-addr.arpa

客户端的主机IP地址可能与客户端的专用网络外部的主机IP地址不匹配。我们在“ [网络地址转换器”](http://www.bittorrent.org/beps/bep_0022.html#network-address-translators)部分中解决此问题 。

此示例返回的PTR资源记录包含域名

adsl-69-107-0-14.dsl.pltn13.pacbell.net

然后，客户端在以下位置查找SRV记录

_bittorrent-tracker._tcp.adsl-69-107-0-14.dsl.pltn13.pacbell.net

如果未找到SRV记录，则按照“ [迭代查询”中的说明进行](http://www.bittorrent.org/beps/bep_0022.html#iterative-queries)一个或多个后续[查询](http://www.bittorrent.org/beps/bep_0022.html#iterative-queries)。

每个返回的SRV资源记录中的目标字段包含跟踪器的域名和运行跟踪器的端口。该跟踪器称为_本地跟踪器_，但是与该跟踪器通信的协议与[[1]中](http://www.bittorrent.org/beps/bep_0022.html#bep-3)描述的标准BitTorrent跟踪器协议没有什么不同。

当BitTorrent客户端加入群集时，它将向.torrent文件中引用的一个或多个跟踪器进行通告，并向本地跟踪器进行通告。本地跟踪器将对等方（可能是缓存或声明相同文件的其他对等方）返回给本地跟踪器。

客户可以优先对待附近的同伴或优先缓存。

反向DNS查找在RFC 1034 [[4]](http://www.bittorrent.org/beps/bep_0022.html#rfc-1034)中描述。SRV资源记录类型在RFC 2782 [[6]中](http://www.bittorrent.org/beps/bep_0022.html#rfc-2782)描述。

## 迭代查询

从反向DNS查找返回的域名特定于查询主机。在DNS的简单实施中，每个查询主机都会有一个SRV资源记录。这会起作用，但很麻烦。一种自然的，看似不那么繁重的但不正确的解决方案是使用以下形式的通配符：

* .pacbell.net

如果通配符是根据[[4]中](http://www.bittorrent.org/beps/bep_0022.html#rfc-1034) 4.3.2节中的算法实现的，则pacbell.net的所有不具有完全匹配的标签的子域都将与通配符匹配。因此，除非存在完全匹配，否则查询

_bittorrent-tracker._tcp.adsl-69-107-0-14.dsl.pltn13.pacbell.net

和

_jabber._tcp.pacbell.net

两者都匹配* .pacbell.net，并且所有具有所有者* .pacbell.net的SRV资源记录都将返回，且名称设置为查询中的名称。因此，如果没有更多信息，就不可能将Jabber与BitTorrent SRV记录区分开。BIND 9.4.1实现了此行为。

另一个自然但不正确的解决方案是指定该类型的域名

_bittorrent-tracker._tcp。*。pacbell.net

[[4]中的](http://www.bittorrent.org/beps/bep_0022.html#rfc-1034) 4.3.3节指定通配符仅作为域名中的第一个标签出现。[[7]中](http://www.bittorrent.org/beps/bep_0022.html#rfc-4592)取消了此限制 ，但不适用于我们的用例的语义。不在域名开头的星号不会被视为通配符。仅查找确切的域名

_bittorrent-tracker._tcp。*。pacbell.net

火柴。

我们提出了一种避免通配符并允许子组织覆盖上级组织提供的SRV记录的替代方案：对等方首先使用从反向DNS查找返回的其完全合格的域名进行查询，如果失败，则在删除最多的域名后再次查询域名中的特定（最左侧）标签。例如，如果在查询时没有返回SRV记录

_bittorrent-tracker._tcp.adsl-69-107-0-14.dsl.pltn13.pacbell.net

然后客户查询

_bittorrent-tracker._tcp.dsl.pltn13.pacbell.net

然后

_bittorrent-tracker._tcp.pltn13.pacbell.net

搜索会一次删除一个标签，该标签会在找到一个或多个资源记录时终止，或者在查询不是ccTLD的根域或顶级域（例如.com，.org，.net）之前终止。考虑到全局定义缓存的可能性很小，因此我们避免查询根域或顶级域，因此客户端将不必要地在根域域名服务器上加重查询，从而产生负面结果。我们考虑过在查询国家/地区级域名之前先停止，但是提供公共基础结构的国家可能会选择提供缓存。

## 网络地址转换器

Internet上的许多主机都位于通过网络地址转换器（NAT）连接到Internet的专用网络中。此类主机可能具有从IANA定义的私有IP地址范围之一分配的IP地址，例如，范围为前缀10 / 8、172.16 / 12和192.168 / 16。与专用网络外部的主机进行通信时，NAT会将专用IP转换为可全局路由的IP地址。该全局可路由地址是主机的_外部IP地址_。

BitTorrent客户端必须使用其主机的外部IP地址。BitTorrent客户端可以从实现BEP 24 [[3]](http://www.bittorrent.org/beps/bep_0022.html#bep-24)的跟踪器返回的_外部ip_密钥，或从实现为[[2]中](http://www.bittorrent.org/beps/bep_0022.html#bep-10)提议的_扩展协议_定义的_yourip_扩展的对等方获得的外部IP 密钥， 获取其主机的外部IP 。[](http://www.bittorrent.org/beps/bep_0022.html#bep-24)[](http://www.bittorrent.org/beps/bep_0022.html#bep-10)

## 例

在我们的示例中，我们使用AT＆T的PacBell网络。通过将以下行添加到pacbell.net的区域文件中，AT＆T可以实现跟踪器发现，

; 名称ttl cls rr pri重量端口目标
_bittorrent-tracker._tcp.pacbell.net。600 IN SRV 5 0 6969跟踪器

现在，当客户端执行跟踪器发现时，它会执行三个DNS查询，在到达域名pacbell.net之前先删除标签，然后返回SRV记录，然后客户端查询tracker.pacbell.net以获取缓存的域名。

在Python中，可以使用PyDNS使用以下代码获取本地跟踪器的端口和域：

```python
import DNS

tlds = ["com", "net", "org"]  # add more TLDs here.

name = DNS.revlookup( "69.107.0.14" )
names = name.split('.')
while names and names[0] not in tlds:
   name = "_bittorrent-tracker._tcp." + ".".join(names)
   req = DNS.Request( name=name, qtype="SRV", protocol="udp")
   response = req.req()
   if response.answers:
      break
   del names[0]

print "response=", response.show()
```

这可能会产生类似的输出

```
response= ; <<>> PDG.py 1.0 <<>> _bittorrent._tcp.pacbell.net SRV
;; options: recurs
;; got answer:
;; ->>HEADER<<- opcode 0, status NOERROR, id 0
;; flags: qr aa rd ra; Ques: 1, Ans: 1, Auth: 2, Addit: 3
;; QUESTIONS:
;;      _bittorrent-tracker._tcp.pacbell.net, type = SRV, class = IN

;; ANSWERS:
_bittorrent-tracker._tcp.pacbell.net    600    SRV     (5, 0, 6969, 'cache.pacbell.net')

;; AUTHORITY RECORDS:
pacbell.net             86400   NS      ns1.pbi.net
pacbell.net             86400   NS      ns2.pbi.net

;; ADDITIONAL RECORDS:
cache.pacbell.net       86400   A       69.107.0.1
ns1.pacbell.net         86400   A       206.13.28.11
ns2.pacbell.net         86400   A       206.13.29.11

;; Total query time: 0 msec
;; To SERVER: localhost
;; WHEN: Mon May 19 16:00:12 2008

```

上面的答案是虚构的，因为AT＆T目前不为BitTorrent跟踪器实现SRV记录。

在Microsoft Windows中，可以使用WinDNS（Dnsapi.lib）和DnsQuery（）获得服务器的端口和域名。在Unix中，相关的调用是来自libresolv的res_query（）。

