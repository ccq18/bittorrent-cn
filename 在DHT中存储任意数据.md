# 在DHT中存储任意数据

http://www.bittorrent.org/beps/bep_0044.html

 

## 抽象

通过此扩展，可以在BitTorrent DHT [[1]中](http://www.bittorrent.org/beps/bep_0044.html#bep-5)存储和检索任意数据。它既支持存储不可变项（其中密钥是数据本身的SHA-1散列），也支持可变项（其中密钥是用于对数据进行签名的密钥对的公钥）。

## 基本原理

BEP 5 [[1]](http://www.bittorrent.org/beps/bep_0044.html#bep-5)定义的DHT 仅提供存储和检索与哈希关联的IP地址的功能。但是，还有许多其他类型的数据可能对存储在DHT中有用。此扩展定义了一个协议，该协议使新功能可以将DHT用作通用键/值存储。

## 术语

在本文档中，_存储节点_是指DHT中要向其宣告和存储项目的节点。一个_请求节点_是指这使得查找UPS在DHT从中找到存储节点，以请求的项目节点，并可能重新公布这些项目，让他们活着。

## 留言内容

建议的新消息<tt class="docutils literal">get</tt>和<tt class="docutils literal">put</tt>与现有的<tt class="docutils literal">get_peers</tt>和<tt class="docutils literal">announce_peer</tt>相似。对<tt class="docutils literal">get的</tt>响应应始终包括<tt class="docutils literal">node</tt>和<tt class="docutils literal">node6</tt>。这些字段的语义与<tt class="docutils literal">get_peers</tt>响应中的语义相同。它还应包括一个写令牌<tt class="docutils literal">token</tt>，其语义与<tt class="docutils literal">get_peers中</tt>的相同。写令牌可以专门绑定到<tt class="docutils literal">被</tt>请求的密钥。即<tt class="docutils literal">令牌</tt>只能用于存储该键下的值。它也可以绑定到请求节点的节点ID和IP地址。

这些消息中的<tt class="docutils literal">id</tt>字段具有与标准DHT消息相同的语义，即发送消息的节点的节点ID，以维护DHT网络的结构。

当分别请求一个项目和编写一个项目时，<tt class="docutils literal">令牌</tt>字段还具有与标准DHT消息<tt class="docutils literal">get_peers</tt>和<tt class="docutils literal">announce_peer</tt>相同的语义。

所述<tt class="docutils literal">ķ</tt>字段是32字节ed25519公开密钥，这些签名可以与被认证。查找可变项时，<tt class="docutils literal">目标</tt>字段必须是此键与<tt class="docutils literal">salt</tt>（如果存在）串联的SHA-1哈希。

存储可变项和不可变项之间的区别是包含公共密钥，序列号，签名和可选的salt（<tt class="docutils literal">k</tt>，<tt class="docutils literal">seq</tt>，<tt class="docutils literal">sig</tt>和<tt class="docutils literal">salt</tt>）。

<tt class="docutils literal">获取</tt>对可变项和不可变项的请求可能无法彼此区分。一个实现可以将可变项和不可变项内部存储在同一哈希表中，也可以存储在单独的哈希表中，并有可能对<tt class="docutils literal">get</tt>请求进行两次查找。

的<tt class="docutils literal">v</tt>字段是_值_被存储。允许为任何bencoded类型（列表，字典，字符串或整数）。当对其进行哈希处理（用于验证其签名或计算其密钥）时，将使用其扁平化，本编码的形式。如果<tt class="docutils literal">放置</tt>请求中的值包含无效的bencoding（例如，带有未排序键的字典），则存储节点务必拒绝该请求，并应返回一条错误消息，其代码为203。

存储节点可以拒绝<tt class="docutils literal">v</tt>的bencoded形式超过1000个字节的<tt class="docutils literal">put</tt>请求。换句话说，假设存储成功超过1000个字节是不安全的。

## 不变物品

不可变项存储在其SHA-1哈希下，并且由于无法对其进行修改，因此无需验证其来源。这使不可变项变得简单。

进行查询的节点应验证其从网络接收的数据，以验证其哈希值是否与所查询的目标匹配。

### 放留言

请求：


```
{
    "a":
    {
        "id": <20 byte id of sending node (string)>,
        "token": <write-token (string)>,
        "v": <any bencoded type, whose encoded size <= 1000>
    },
    "t": <transaction-id (string)>,
    "y": "q",
    "q": "put"
}
```

响应：

```
{
    "r": { "id": <20 byte id of sending node (string)> },
    "t": <transaction-id (string)>,
    "y": "r",
}
```

### 得到消息

请求：

```
{
    "a":
    {
        "id": <20 byte id of sending node (string)>,
        "target": <SHA-1 hash of item (string)>,
    },
    "t": <transaction-id (string)>,
    "y": "q",
    "q": "get"
}
```
响应：

```
{
    "r":
    {
        "id": <20 byte id of sending node (string)>,
        "token": <write token (string)>,
        "v": <any bencoded type whose SHA-1 hash matches 'target'>,
        "nodes": <IPv4 nodes close to 'target'>,
        "nodes6": <IPv6 nodes close to 'target'>
    },
    "t": <transaction-id>,
    "y": "r",
}
```

## 可变物品

可变项可以更新，而无需更改其DHT键。为了验证只有原始发布者可以更新项目，该项目由原始发布者生成的私钥签名。目标ID可变项存储在公共密钥的SHA-1散列下（如它出现在<tt class="docutils literal">put</tt>消息中）。

为了避免恶意节点用旧版本覆盖列表头，每次更新的序列号<tt class="docutils literal">seq</tt>必须单调增加，并且托管列表节点的节点不得将列表头从较高的序列号降级为较低的序列号一，只能升级。序列号不应超过<tt class="docutils literal">MAX_INT64</tt>，即<tt class="docutils literal">0x7fffffffffffffffff</tt>。客户端可以拒绝任何序列号超出此范围的消息。客户也可以拒绝任何带有负序号的消息。

该签名是与<tt class="docutils literal">v</tt>键连接的经编码的序列号的64字节ed25519签名。例如这样的事情：

3：seqi4e1：v12：您好！

如果<tt class="docutils literal">盐</tt>键存在且非空，则盐字符串必须包含在已签名的内容中。请注意，如果指定了<tt class="docutils literal">salt</tt>且为空字符串，则好像没有指定<tt class="docutils literal">盐</tt>一样，除了序列号和数据外没有其他内容。盐串不得超过64个字节。

当签名中包含<tt class="docutils literal">盐时，</tt>带有键值的键<tt class="docutils literal">盐</tt>将以其bencoded形式开头。例如，如果<tt class="docutils literal">salt</tt>是“ foobar”，则要签名的缓冲区是：

4：salt6：foobar3：seqi4e1：v12：Hello world！

### 放留言

请求：

```
{
    "a":
    {
        "cas": <optional expected seq-nr (int)>,
        "id": <20 byte id of sending node (string)>,
        "k": <ed25519 public key (32 bytes string)>,
        "salt": <optional salt to be appended to "k" when hashing (string)>
        "seq": <monotonically increasing sequence number (integer)>,
        "sig": <ed25519 signature (64 bytes string)>,
        "token": <write-token (string)>,
        "v": <any bencoded type, whose encoded size < 1000>
    },
    "t": <transaction-id (string)>,
    "y": "q",
    "q": "put"
}
```

存储节点接收到的<tt class="docutils literal">seq</tt>小于或等于节点上已存储的<tt class="docutils literal">放置</tt>请求的节点，必须拒绝该请求。如果序列号相等，并且值也相同，则节点应该重置其超时计数器。

如果<tt class="docutils literal">放置</tt>消息中的序列号小于与当前存储的值关联的序列号，则存储节点可以返回一条错误代码为302的错误消息（参见下面的错误代码）。

请注意，此请求不包含目标哈希。<tt class="docutils literal">k</tt>参数隐含了存储此Blob的目标哈希。密钥是密钥（<tt class="docutils literal">k</tt>）的SHA-1哈希。

为了支持用于在DHT中存储单独项目的单个密钥，可以在可变项目的<tt class="docutils literal">放置</tt>请求中指定可选的<tt class="docutils literal">盐</tt>。

如果盐条目不存在，则可以假定它是一个空字符串，并且其语义应与指定带有空字符串的盐键相同。

盐可以是任何二进制字符串（但最方便的是某种东西的哈希）。当计算存储下面的blob的密钥时（即，密钥<tt class="docutils literal">get</tt>请求指定检索此数据），此字符串将附加到密钥，如<tt class="docutils literal">k</tt>字段中所指定。

这使一个具有单个密钥的实体可以发布任意数量的不相关项，并具有一个供读者验证的单个密钥。如果发布者事先不知道要发布多少个不同的项目，这将很有用。它可以为用户分发单个公钥以验证已发布的Blob。

请注意，盐不会在对<tt class="docutils literal">get</tt>请求的响应中返回。这是故意的。发出项目的<tt class="docutils literal">获取</tt>请求时，期望知道盐是什么（因为它是所查找的目标ID的一部分）。无需重复此操作以供旁观者查看。

#### 中国科学院

CAS是_比较和交换的_缩写，它的语义与CAS CPU指令相似。当多个节点写入DHT中的同一插槽时，它用于避免争用情况。

在<tt class="docutils literal">中科院</tt>字段是可选的。如果存在，它指定被put覆盖的数据blob的序列号。如果存在，则存储节点必须将此编号与其在该密钥下存储的当前序列号进行比较。仅当<tt class="docutils literal">cas</tt>与存储的序列号匹配时，才执行put。如果不匹配，则存储将失败，并且必须返回错误。请参阅下面的[错误](http://www.bittorrent.org/beps/bep_0044.html#errors)。

在<tt class="docutils literal">中科院</tt>字段仅适用于可变看跌期权。如果没有当前值，则应忽略<tt class="docutils literal">cas</tt>字段。

当发送<tt class="docutils literal">放</tt>请求到没有为返回任何数据的节点<tt class="docutils literal">获取</tt>，在<tt class="docutils literal">CAS</tt>领域不应该被包括在内。

### 响应

响应：

```
{
    "r": { "id": <20 byte id of sending node (string)> },
    "t": <transaction-id (string)>,
    "y": "r",
}
```

### 失误

如果存储由于任何原因失败，将返回错误消息，而不是上面的消息模板，即其中“ y”为“ e”且“ e”为[错误代码，消息]的元组的消息）。失败包括<tt class="docutils literal">cas</tt>不匹配，并且序列号已过时。

错误消息（由BEP 5 [[1]](http://www.bittorrent.org/beps/bep_0044.html#bep-5)指定）如下所示：

```
{
    "e": [ <error-code (integer)>, <error-string (string)> ],
    "t": <transaction-id (string)>,
    "y": "e",
}
```

除了BEP 5中定义的错误代码外，本规范还定义了一些其他错误代码。

| 错误代码 | 描述 |
| --- | --- |
| 205 | 讯息（<tt class="docutils literal">v</tt>栏位）太大。 |
| 206 | 无效签名 |
| 207 | 盐（<tt class="docutils literal">盐场</tt>）太大。 |
| 301 | CAS哈希不匹配，请重新读取值，然后重试。 |
| 302 | 序列号小于当前。 |

如果cas不匹配，则实现必须发出301错误。这是同步多个共享可变项的代理程序的关键功能。

### 得到消息

请求：

```
{
    "a":
    {
        "id": <20 byte id of sending node (string)>,
        "seq": <optional sequence number (integer)>,
        "target:" <20 byte SHA-1 hash of public key and salt (string)>
    },
    "t": <transaction-id (string)>,
    "y": "q",
    "q": "get"
}
```

可选的<tt class="docutils literal">seq</tt>字段指定仅当项目的序列号大于给定值时，才发送该项目的值。如果存在已存储的项目，但是其序列号小于或等于<tt class="docutils literal">seq</tt>字段，则应从响应中省略<tt class="docutils literal">k</tt>，<tt class="docutils literal">v</tt>和<tt class="docutils literal">sig</tt>字段。

响应：

```
{
    "r":
    {
        "id": <20 byte id of sending node (string)>,
        "k": <ed25519 public key (32 bytes string)>,
        "nodes": <IPv4 nodes close to 'target'>,
        "nodes6": <IPv6 nodes close to 'target'>,
        "seq": <monotonically increasing sequence number (integer)>,
        "sig": <ed25519 signature (64 bytes string)>,
        "token": <write-token (string)>,
        "v": <any bencoded type, whose encoded size <= 1000>
    },
    "t": <transaction-id (string)>,
    "y": "r",
}
```

## 签名验证

为了最大程度地攻击本编码解析器，应按如下所示对值和序列号进行签名和验证：

1.  分别编码值和序列号。
2.  连接（“ 4：盐”盐_长_ “：” _盐_）“ 3：seqi” _seq_ “ e1：v” _len_ “：”和编码值。值“ Hello World！”的序列号1。将被转换为：“ 3：seqi1e1：v12：Hello World！”。这样，即使解析器包含某些错误，也无法说服节点该长度的一部分实际上是序列号的一部分。此外，如果bencoding序列化程序更改字典中条目的顺序，则不可能出现验证失败。盐在括号中，因为它是可选的。仅在<tt class="docutils literal">放置</tt>请求中指定了非空盐时，才添加该前缀。
3.  签名或验证串联的字符串。

在存储节点上，必须在接受store命令之前验证签名。数据必须存储在公共密钥的SHA-1散列（如在本编码字典中显示）和盐（如果存在）的下面。

在请求节点上，必须验证从<tt class="docutils literal">获取</tt>请求中获取的密钥，以将其哈希到查找所针对的目标ID，并验证签名。如果这些失败，则应将响应视为无效。

## 期满

未经重新发布，这些项目可能会在2小时后失效。为了使物品活着，应该每小时重新发布一次。

任何有兴趣在DHT中保持斑点的节点都可以宣布它。它将简单地重复签名以获得可变的放置权，而无需使用私钥。这样即使最初的发布者离开了，也只有在用新数据替换时才联机，数据才能保留下来。

为了减少写入流量，如果在查找查询时满足以下所有条件，则订户不需要重新发布该值：

1.  他们发现了8个以上的数据副本
2.  距离目标密钥最近的8个有资格进行存储的节点都通过返回数据或通过<tt class="docutils literal">seq</tt>编号表示它们具有数据。
3.  对于可变项，只有具有最新已知序列号的值的节点才计入满足这些条件的条件

这里的假设是实现的不准确性，搅动和数据包丢弃会导致不同的节点看到一组稍微不同的最近节点，从而发布到不同的节点。因此，最接近的节点的最新集合加上超出该集合的过多存储值，表明存在多个重新发布者。

订户还可以将值持久保存到永久存储中，以便在重新启动后重新发布它们。

## 测试向量

### 测试1（可变）

值：

12:Hello World!

缓冲区被签名：

3:seqi1e1:v12:Hello World!

公钥：

77ff84905a91936367c01360803104f92432fcd904a43511876df5cdf3e7e548

私钥：


e06d3183d14159228433ed599221b80bd0a5ce8352e4bdf0262f76786ef1c74d
b7e7a9fea2c0eb269d61e3b38e450a22e754941ac78479d6c54e1faf6037881d

**目标ID**：

4a533d47ec9c7d95b1ad75f576cffc641853b750

**签名**：

305ac8aeb6c9c151fa120f120ea2cfb923564e11552d06a5d856091e5e853cff
1260d3f39e4999684aa92eb73ffd136e6f4f3ecbfda0ce53a1608ecd7ae21f01

### 测试2（用盐可变）

值：

12:Hello World!

salt：

foobar

缓冲区被签名：

4:salt6:foobar3:seqi1e1:v12:Hello World!

公钥：

77ff84905a91936367c01360803104f92432fcd904a43511876df5cdf3e7e548

私钥：

e06d3183d14159228433ed599221b80bd0a5ce8352e4bdf0262f76786ef1c74d
b7e7a9fea2c0eb269d61e3b38e450a22e754941ac78479d6c54e1faf6037881d

**目标ID**：

411eba73b6f087ca51a3795d9c8c938d365e32c1

**签名**：

6834284b6b24c3204eb2fea824d82f88883a3d95e8b4a21b8c0ded553d17d17d
df9a8a7104b1258f30bed3787e6cb896fca78c58f8e03b5f18f14951a87d9a08

### 测试3（不变）

值：

12:Hello World!

**目标ID**：

e5f96f6f38320f0f33959cb4d3d656452117aadb

## 资源资源

该文档大量源自libtorrent [[2]中](http://www.bittorrent.org/beps/bep_0044.html#dht-store)包含的扩展文档。在许多地方，文本只是被复制和修改。

实现ed25519 DSA的库：

*   [NaCl](http://nacl.cr.yp.to/)
*   [libsodium](https://github.com/jedisct1/libsodium)
*   [nightcracker's ed25519](https://github.com/nightcracker/ed25519)