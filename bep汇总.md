# bep汇总

http://www.bittorrent.org/beps/bep_0000.html 汇总

http://www.bittorrent.org/beps/bep_0001.html BEP 代表 BitTorrent 增强提案。BEP 是向 BitTorrent 社区提供信息或描述 BitTorrent 协议新功能的设计文档。BEP 应提供功能的简明技术规范和功能的基本原理。

https://www.bittorrent.org/beps/bep_0002.html Bep模板

http://www.bittorrent.org/beps/bep_0003.html **BitTorrent 协议规范**：种子文件结构，对等协议，对等消息

https://www.bittorrent.org/beps/bep_0004.html 本文档描述了 BitTorrent 协议的已知位分配和消息 ID

[http://www.bittorrent.org/beps/bep_0005.html](http://www.bittorrent.org/beps/bep_0005.html) **DHT协议**

https://www.bittorrent.org/beps/bep_0006.html 快速扩展

https://www.bittorrent.org/beps/bep_0009.html **对等发送元数据文件的扩展** 此扩展的目的是允许客户端加入群并完成下载，而无需先下载 .torrent 文件。此扩展允许客户端从对等点下载元数据。它使得支持_磁力链接_成为可能，磁力链接是网页上的链接，仅包含足够的信息来加入群（信息哈希）。

https://www.bittorrent.org/beps/bep_0010.html 该协议的目的是为 bittorrent 协议的扩展提供简单而精简的传输。支持此协议可以轻松添加新扩展，而不会干扰标准 bittorrent 协议或不支持此扩展或您要添加的扩展的客户端。

https://www.bittorrent.org/beps/bep_0011.html 一旦对等节点通过其他机制（例如 DHT 或 Tracker 公告）进行引导，对等交换 (PEX) 就会为群提供替代的对等发现机制。 它提供了比大多数其他来源更新的群视图，并且还减少了频繁查询其他来源的需要

https://www.bittorrent.org/beps/bep_0012.html 多跟踪器元数据扩展

https://www.bittorrent.org/beps/bep_0015.html 用于 BitTorrent 的 UDP 跟踪器协议

https://www.bittorrent.org/beps/bep_0019.html HTTP/FTP 播种 HTTP 或 FTP 服务器充当永久未阻塞的种子。

https://www.bittorrent.org/beps/bep_0023.html 为了减少跟踪器响应的大小并减少跟踪器中的内存和计算要求，跟踪器可能会以打包字符串而不是编码列表的形式返回对等点。https://www.bittorrent.org/beps/bep_0027.html 私有种子

https://www.bittorrent.org/beps/bep_0029.html **uTorrent 传输协议**

http://www.bittorrent.org/beps/bep_0055.html 打孔扩展 提供了一种连接到无法接收入站连接的对等点的方法，无论它们是在过滤 NAT 后面还是在阻止传入连接的防火墙后面。