# 同行交流（PEX）.md
http://www.bittorrent.org/beps/bep_0011.html


一旦对等方通过DHT或Tracker宣布之类的其他机制自举，对等交换（PEX）为群体提供了另一种对等发现机制。

与大多数其他来源相比，它提供了最新的群集视图，并且还减少了频繁查询其他来源的需求。

当与BEP 40 [[1]](http://www.bittorrent.org/beps/bep_0011.html#bep-40)结合使用时，它提供了一种快速随机化群集连接图的方法。

## 协议扩展

PEX 通过扩展协议[[2]](http://www.bittorrent.org/beps/bep_0011.html#bep-10)引入了新消息<tt class="docutils literal">ut_pex</tt>。[](http://www.bittorrent.org/beps/bep_0011.html#bep-10)

添加了在握手中协商的消息：

```
{
  m: {
    ut_pex: <implementation-dependent local message ID (positive integer)>,
    ...
  },
  ...
}
```

扩展消息本身由bittorrent /扩展消息标头和以下按本国编码的有效内容组成：

```
{
  added: <one or more contacts in IPv4 compact format (string)>
  added.f: <optional, bit-flags, 1 byte per added IPv4 peer (string)>
  added6: <one or more contacts IPv6 compact format (string)>,
  added6.f: <optional, bit-flags, 1 byte per added IPv6 peer (string)>,
  dropped: <one or more contacts in IPv6 compact format (string)>,
  dropped6: <one or more contacts in IPv6 compact format (string)>
}
```

标志定义如下：


 | Bit | 设置时机 |
 | --- | --- |
 | 0x01 | 更喜欢加密，如扩展握手中的<tt class="docutils literal">e</tt>字段所示 |
 | 0x02 | 仅种子/上传 |
 | 0x04 | 支持uTP |
 | 0x08 | 对等点表示扩展握手中支持<tt class="docutils literal">ut_holepunch</tt> |
 | 0x10 | 传出连接，对等体可以访问 |

其他位保留供将来使用。如果实施者打算引入新的标志，则应提交修改此BEP的请求。

成功建立连接后，对等方只能包括在<tt class="docutils literal">添加的</tt>字段中，而当断开连接时，则必须包括在<tt class="docutils literal">丢弃的</tt>字段中。一旦<tt class="docutils literal">添加</tt>了对等方，客户端必须确保在适当的时候发送相应的<tt class="docutils literal">丢弃</tt>事件。仅发信号通知添加的对等方而不丢弃它们是不兼容的行为。

> **原理**：PEX旨在反映客户端_当前连接到_哪个对等_方_，从而确保PEX提供比其他对等方发现机制更好的活动信息。
> 
> **理由2**：仅传播经过验证的对等方，可以减少攻击者滥用bittorrent群以进行分布式拒绝服务攻击的机会。

客户端必须批量更新，才能每分钟发送不超过1个PEX消息。

握手后不需要立即发送PEX消息，例如，在torrent启动期间，客户端可以等待，直到它建立了足够的连接以使发送pex消息值得。

添加或删除的联系人不得包含重复项。

只要更新消息不影响正确性，就可以忽略它们之间的瞬时连接断开连接或断开连接重新连接事件。

> **实施说明**：一种简单的方法是为每个已连接的对等设备排队尚未发送的连接/断开事件，并在生成消息时执行省略。稍微复杂一点但更节省内存的方法是保留每个torrent事件的连接/断开事件时间轴，并简单地存储指向每个对等方已发送事件的时间点的指针。创建PEX消息时，它们只需要前进指针，注意避免重复，并消除瞬态连接。

添加的联系人不得在同一封邮件中删除。

除初始PEX消息外，添加的v4 / v6联系人的总数量不应超过50个条目。删除条目也是如此。

邮件必须至少包含以下字段之一：<tt class="docutils literal">add，added6，dropd，dropd6</tt>。

客户可能断开严重违反这些约束的对等方。

## 填充人口不足的列表

的组合

*   高于活力要求
*   断开种子或种子部分[[3]](http://www.bittorrent.org/beps/bep_0011.html#bep-21)同时播种
*   根据ipv4和ipv6之间的对等体ID断开重复的对等体

可能会导致人口不足的<tt class="docutils literal">添加</tt>或<tt class="docutils literal">添加</tt>列表6。这个问题经常出现在以种子为主导的群体中，那里的种子没有活生生的种子可以繁殖，而同龄人只有可以繁殖到其他种子的种子，大大降低了PEX的效力。同样，由于ipv6连接将被视为已经建立的v4连接的副本，因此这可能会使在ipv4主导的群集中很难获得ipv6对等体，从而阻止了它们通过PEX传播。

为了解决这些问题，如果某个特定地址族的一个客户端连接到少于25个客户端，则放宽对活动性的要求。在这种情况下，它可能_会_为该地址族保留最多25个最近建立的_完全握手_连接的列表，并记录这些连接的断开原因。本地发起的断开连接的以下原因使远程联系人有资格包含在<tt class="docutils literal">添加</tt>或<tt class="docutils literal">添加的</tt>列表中：

*   同一对等ID已在不同地址族下连接
*   永久缺乏共同的利益，例如从（部分）种子状态和可得性推断
*   超出了本地资源限制，例如全局连接数

当在pex消息中包括最近断开的联系人时，必须将其从最近看到的列表中删除，以便在下一条消息中不再将其发送。当列表通过瞬态连接断开事件重新填充时，如果满足所有必要条件，则可能会将这些包含在下一条消息中。换句话说，除了从最近看到的列表中填充初始pex消息外，客户端还可以有效地跳过某些连接断开选择。

但是由于最近看到的联系人不代表实时连接，因此必须在下一条PEX消息中将其删除。

仍然必须保持以下限制：不得在同一消息中添加和删除同一地址。

选择不超过25个实时连接的要求和25个最近见过的连接的要求，以使最多可以累积两个可放置联系人的pex消息，并且当有足够的实时联系人来填充pex消息时，不会发送过时的信息。

请注意，此豁免可以分别应用于IPv4和IPv6。即，即使有足够的v4实时联系人，如果各个列表的人口不足，客户仍可能包括最近见过的v6联系人，反之亦然。

## 安全注意事项

通过PEX消息交换的数据应被认为是不可信的，并且可能是恶意的。

攻击者可能试图通过使虚假的或其他不合作的同伴淹没来破坏它们。

PEX还可以通过诱使bittorrent客户端执行到受害IP范围的连接尝试来引起分布式拒绝服务攻击。

为了缓解这些问题，客户端应避免从单个PEX来源获取其所有候选连接。重复的IP地址（例如，具有不同的端口）应被忽略。另外，规范对等优先级[[1]](http://www.bittorrent.org/beps/bep_0011.html#bep-40)可以帮助将连接尝试分布在许多子网中，从而减少对任何潜在的受害子网的影响。