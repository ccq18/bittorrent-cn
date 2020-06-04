# 备用BitTorrent缓存发现协议

http://www.bittorrent.org/beps/bep_0025.html

 

## 动机

某些Internet服务提供商（ISP）可能希望部署BitTorrent缓存以降低传输成本，减少内部流量并通过加快下载速度来改善用户体验。

缓存只是网络中间的一个快速对等体。它还可能具有大量的磁盘空间。客户端使用普通的BitTorrent协议与缓存进行通信。

通过此扩展，BitTorrent客户端能够发现网络附近的缓存。当存在高速缓存时，用户将受益于拥有高容量的对等方，用户的客户端可以从该对等方下载并且可以委托其播种。当用户的ISP网络内部的缓存代表客户端播种时，它释放了用户访问网络中的上游容量，使用户和共享访问网络的用户受益。当后续的对等方从其ISP的缓存中传输时，ISP的传输流量将减少。

与域名系统（DNS）和现有标准的预期用途相比，这比BEP-22 [[3]中](http://www.bittorrent.org/beps/bep_0025.html#bep-22)提出的替代方案更简单 。

## 发现机制

为了找到其ISP的缓存，BitTorrent客户端对其外部IP地址执行反向DNS查找，并在其前面加上“ bittorrent-tracker”，然后解析结果域名以找到该跟踪器。例如，地址为69.107.0.14的主机在以下位置获取PTR记录

14.0.107.69.in-addr.arpa

客户端的主机IP地址可能与客户端的专用网络外部的主机IP地址不匹配。我们在“ [网络地址转换器”](http://www.bittorrent.org/beps/bep_0025.html#network-address-translators)部分中解决此问题 。

此示例返回的PTR资源记录包含域名

adsl-69-107-0-14.dsl.pltn13.pacbell.net

客户端然后解析域名

bittorrent-tracker.adsl-69-107-0-14.dsl.pltn13.pacbell.net

如果未找到IP地址，则按照“ [迭代查询”中的说明进行](http://www.bittorrent.org/beps/bep_0025.html#iterative-queries)一个或多个后续[查询](http://www.bittorrent.org/beps/bep_0025.html#iterative-queries)。

返回的跟踪器称为_缓存跟踪器_，但是与这些跟踪器通信的协议与[[1]中](http://www.bittorrent.org/beps/bep_0025.html#bep-3)描述的标准BitTorrent跟踪器协议没有什么不同。

当BitTorrent客户端加入群集时，它将向.torrent文件中引用的一个或多个跟踪器进行通告，并向缓存跟踪器进行通告。高速缓存跟踪器将可能是高速缓存的对等方或宣布相同文件的其他对等方返回给高速缓存跟踪器。

缓存是一个BitTorrent对等体。客户可以优先对待它。

反向DNS查找在RFC 1034 [[5]中](http://www.bittorrent.org/beps/bep_0025.html#rfc-1034)进行了描述。

## 迭代查询

从反向DNS查找返回的域名特定于查询主机。在DNS的简单实施中，每个查询主机都会有一个bittorrent-tracker A或AAAA资源记录。最明显的解决方案是使用以下形式的通配符：

bittorrent-tracker。*。pacbell.net

但是，[[5]中的](http://www.bittorrent.org/beps/bep_0025.html#rfc-1034) 4.3.3节指定通配符仅作为域名中的第一个标签出现。[[7]中](http://www.bittorrent.org/beps/bep_0025.html#rfc-4592)取消了此限制，但不适用于我们的用例的语义。不在域名开头的星号不会被视为通配符。仅查找确切的域名

bittorrent-tracker。*。pacbell.net

火柴。

我们提出了一种避免通配符并允许子组织覆盖上级组织提供的映射的替代方法：对等方首先使用从反向DNS查找返回的完全限定域名进行查询，如果失败，则在删除最特定的域名后再次查询域名中（最左侧）标签。例如，如果在查询时没有返回A / AAAA记录

bittorrent-tracker.adsl-69-107-0-14.dsl.pltn13.pacbell.net

然后客户查询

bittorrent-tracker.dsl.pltn13.pacbell.net

然后

bittorrent-tracker.pltn13.pacbell.net

搜索会一次删除一个标签，该标签会在找到一个或多个资源记录时终止，或者在查询不是ccTLD的根域或顶级域（例如.com，.org，.net）之前终止。考虑到全局定义缓存的可能性很小，因此我们避免查询根域或顶级域，因此客户端将不必要地在根域域名服务器上加重查询，从而产生负面结果。我们考虑过在查询国家/地区级域名之前先停止，但是提供公共基础结构的国家可能会选择提供缓存。

## 网络地址转换器

Internet上的许多主机都位于通过网络地址转换器（NAT）连接到Internet的专用网络中。此类主机可能具有从IANA定义的私有IP地址范围之一分配的IP地址，例如，范围为前缀10 / 8、172.16 / 12和192.168 / 16。与专用网络外部的主机进行通信时，NAT会将专用IP转换为可全局路由的IP地址。该全局可路由地址是主机的_外部IP地址_。

查找缓存时，BitTorrent客户端必须使用其主机的外部IP地址。BitTorrent客户端可以从从实现BEP 24 [[4]](http://www.bittorrent.org/beps/bep_0025.html#bep-24)的跟踪器返回的_外部ip_密钥或使用 为[[2]中](http://www.bittorrent.org/beps/bep_0025.html#bep-10)建议的_扩展协议_定义的_yourip_扩展从对等方获取其主机的外部IP 。[](http://www.bittorrent.org/beps/bep_0025.html#bep-24)[](http://www.bittorrent.org/beps/bep_0025.html#bep-10)

## 例

在我们的示例中，我们使用AT＆T的PacBell网络。通过将以下行添加到pacbell.net的区域文件中，AT＆T可以实现缓存发现，

bittorrent-tracker.pacbell.net。在A 206.13.28.15

现在，当客户端执行缓存发现时，它将执行三个DNS查询，然后删除标签，然后再到达域名pacbell.net，此时将返回SRV记录，并且客户端查询tracker.pacbell.net以获取缓存的域名。

在Python中，可以使用以下命令获取缓存跟踪器的地址：

进口插座

tlds = [“ com”，“ net”，“ org”]＃在此处添加更多内容。

名称，别名，ipaddrs = socket.gethostbyaddr（“ 69.107.0.14”）
名称= name.split（'。'）
名称和名称[0]不在tlds中：
   name =“ bittorrent-tracker”。+“。”。join（名称）
   尝试：
     ip = socket.gethostbyname（名称）
     打破
   除了：
     删除名称[0]

打印“ response =”，ip

这可能会产生类似的输出

响应='151.164.129.4'

## 动机

某些Internet服务提供商（ISP）可能希望部署BitTorrent缓存以降低传输成本，减少内部流量并通过加快下载速度来改善用户体验。

缓存只是网络中间的一个快速对等体。它还可能具有大量的磁盘空间。客户端使用普通的BitTorrent协议与缓存进行通信。

通过此扩展，BitTorrent客户端能够发现网络附近的缓存。当存在高速缓存时，用户将受益于拥有高容量的对等方，用户的客户端可以从该对等方下载并且可以委托其播种。当用户的ISP网络内部的缓存代表客户端播种时，它释放了用户访问网络中的上游容量，使用户和共享访问网络的用户受益。当后续的对等方从其ISP的缓存中传输时，ISP的传输流量将减少。

与域名系统（DNS）和现有标准的预期用途相比，这比BEP-22 [[3]中](http://www.bittorrent.org/beps/bep_0025.html#bep-22)提出的替代方案更简单 。

## 发现机制

为了找到其ISP的缓存，BitTorrent客户端对其外部IP地址执行反向DNS查找，并在其前面加上“ bittorrent-tracker”，然后解析结果域名以找到该跟踪器。例如，地址为69.107.0.14的主机在以下位置获取PTR记录

14.0.107.69.in-addr.arpa

客户端的主机IP地址可能与客户端的专用网络外部的主机IP地址不匹配。我们在“ [网络地址转换器”](http://www.bittorrent.org/beps/bep_0025.html#network-address-translators)部分中解决此问题 。

此示例返回的PTR资源记录包含域名

adsl-69-107-0-14.dsl.pltn13.pacbell.net

客户端然后解析域名

bittorrent-tracker.adsl-69-107-0-14.dsl.pltn13.pacbell.net

如果未找到IP地址，则按照“ [迭代查询”中的说明进行](http://www.bittorrent.org/beps/bep_0025.html#iterative-queries)一个或多个后续[查询](http://www.bittorrent.org/beps/bep_0025.html#iterative-queries)。

返回的跟踪器称为_缓存跟踪器_，但是与这些跟踪器通信的协议与[[1]中](http://www.bittorrent.org/beps/bep_0025.html#bep-3)描述的标准BitTorrent跟踪器协议没有什么不同。

当BitTorrent客户端加入群集时，它将向.torrent文件中引用的一个或多个跟踪器进行通告，并向缓存跟踪器进行通告。高速缓存跟踪器将可能是高速缓存的对等方或宣布相同文件的其他对等方返回给高速缓存跟踪器。

缓存是一个BitTorrent对等体。客户可以优先对待它。

反向DNS查找在RFC 1034 [[5]中](http://www.bittorrent.org/beps/bep_0025.html#rfc-1034)进行了描述。

## 迭代查询

从反向DNS查找返回的域名特定于查询主机。在DNS的简单实施中，每个查询主机都会有一个bittorrent-tracker A或AAAA资源记录。最明显的解决方案是使用以下形式的通配符：

bittorrent-tracker。*。pacbell.net

但是，[[5]中的](http://www.bittorrent.org/beps/bep_0025.html#rfc-1034) 4.3.3节指定通配符仅作为域名中的第一个标签出现。[[7]中](http://www.bittorrent.org/beps/bep_0025.html#rfc-4592)取消了此限制，但不适用于我们的用例的语义。不在域名开头的星号不会被视为通配符。仅查找确切的域名

bittorrent-tracker。*。pacbell.net

火柴。

我们提出了一种避免通配符并允许子组织覆盖上级组织提供的映射的替代方法：对等方首先使用从反向DNS查找返回的完全限定域名进行查询，如果失败，则在删除最特定的域名后再次查询域名中（最左侧）标签。例如，如果在查询时没有返回A / AAAA记录

bittorrent-tracker.adsl-69-107-0-14.dsl.pltn13.pacbell.net

然后客户查询

bittorrent-tracker.dsl.pltn13.pacbell.net

然后

bittorrent-tracker.pltn13.pacbell.net

搜索会一次删除一个标签，该标签会在找到一个或多个资源记录时终止，或者在查询不是ccTLD的根域或顶级域（例如.com，.org，.net）之前终止。考虑到全局定义缓存的可能性很小，因此我们避免查询根域或顶级域，因此客户端将不必要地在根域域名服务器上加重查询，从而产生负面结果。我们考虑过在查询国家/地区级域名之前先停止，但是提供公共基础结构的国家可能会选择提供缓存。

## 网络地址转换器

Internet上的许多主机都位于通过网络地址转换器（NAT）连接到Internet的专用网络中。此类主机可能具有从IANA定义的私有IP地址范围之一分配的IP地址，例如，范围为前缀10 / 8、172.16 / 12和192.168 / 16。与专用网络外部的主机进行通信时，NAT会将专用IP转换为可全局路由的IP地址。该全局可路由地址是主机的_外部IP地址_。

查找缓存时，BitTorrent客户端必须使用其主机的外部IP地址。BitTorrent客户端可以从从实现BEP 24 [[4]](http://www.bittorrent.org/beps/bep_0025.html#bep-24)的跟踪器返回的_外部ip_密钥或使用 为[[2]中](http://www.bittorrent.org/beps/bep_0025.html#bep-10)建议的_扩展协议_定义的_yourip_扩展从对等方获取其主机的外部IP 。[](http://www.bittorrent.org/beps/bep_0025.html#bep-24)[](http://www.bittorrent.org/beps/bep_0025.html#bep-10)

## 例

在我们的示例中，我们使用AT＆T的PacBell网络。通过将以下行添加到pacbell.net的区域文件中，AT＆T可以实现缓存发现，

bittorrent-tracker.pacbell.net。在A 206.13.28.15

现在，当客户端执行缓存发现时，它将执行三个DNS查询，然后删除标签，然后再到达域名pacbell.net，此时将返回SRV记录，并且客户端查询tracker.pacbell.net以获取缓存的域名。

在Python中，可以使用以下命令获取缓存跟踪器的地址：

进口插座

tlds = [“ com”，“ net”，“ org”]＃在此处添加更多内容。

名称，别名，ipaddrs = socket.gethostbyaddr（“ 69.107.0.14”）
名称= name.split（'。'）
名称和名称[0]不在tlds中：
   name =“ bittorrent-tracker”。+“。”。join（名称）
   尝试：
     ip = socket.gethostbyname（名称）
     打破
   除了：
     删除名称[0]

打印“ response =”，ip

这可能会产生类似的输出

响应='151.164.129.4'

上面的答案是虚构的，因为AT＆T目前不为BitTorrent跟踪器实现SRV记录。

上面的答案是虚构的，因为AT＆T目前不为BitTorrent跟踪器实现SRV记录。