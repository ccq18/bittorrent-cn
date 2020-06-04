 
http://www.bittorrent.org/beps/bep_0036.html

## 抽象

通过使用torrent文件来发布链接到内容的RSS feed已成为一种惯例。该BEP尝试记录和标准化如何格式化此类RSS feed。

## 术语

出于BEP的目的，术语“洪流链接”将用于标识标识洪流的任何URL。它可以是指向.torrent文件的HTTP或HTTPS URL，也可以是标识torrent信息哈希的[磁力链接](http://www.bittorrent.org/beps/bep0009.html)。

本文档中的关键字“必须”，“不得”，“必须”，“应”，“应禁止”，“应”，“不应”，“建议”，“可以”和“可选”是按照[RFC 2119中的](http://www.ietf.org/rfc/rfc2119.txt)描述进行解释 。

## 客户支持

本节将介绍bittorrent客户端当前支持哪些RSS格式。

 

<colgroup><col width="63%"><col width="20%"><col width="17%"></colgroup>
| client | RSS 2.0 | Atom |
| --- | --- | --- |
| uTorrent | Yes | No |
| Azureus | Yes | No |
| Deluge | Yes | Yes |
| qBittorrent | Yes | No |
| KTorrent | Yes | Yes |
| libtorrent | Yes | Yes |
| Catch | Yes | No |

RSS 2.0是基于rss / channel / item标签的提要。

Atom是基于feed / entry标签的feed。

下表指出了供稿中的_项目_支持哪些标签。仅包含标识洪流的标签，因为它们是关键标签。该<tt class="docutils literal">TTL</tt>标签所用的服务器，以指示用户如何频繁刷新的因子。

 

| client | <ttl> | <enclosure> | <media:content> | <media:hash> | <link> | <torrent> | <guid> |
| --- | --- | --- | --- | --- | --- | --- | --- |
| uTorrent | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Azureus [3] | Yes | Yes | No | No | Yes | No | No |
| Deluge [4] | Yes | Yes | No | No | No | No | No |
| qBittorrent | No | Yes | No | No | No | No | No |
| KTorrent | ? | Yes | No | No | No | No | No |
| libtorrent | Yes | Yes | Yes | No | Yes | No | No |
| Catch [1] | No | Yes | No | No | No | No | No |

 [1]来源[http://code.google.com/p/catch/source/browse/trunk/FeedChecker.m](http://code.google.com/p/catch/source/browse/trunk/FeedChecker.m)

 [2] Azureus允许在描述中使用HTML，但去除标记

 [3]基于[http://azureus.sourceforge.net/plugin_details.php?plugin=rssfeed](http://azureus.sourceforge.net/plugin_details.php?plugin=rssfeed)版本1.3.6的org.kmallan.azureus.rssfeed.Scheduler.java

 [4]使用YaRSS2 [https://github.com/bendikro/deluge-yarss-plugin/blob/master/yarss2/lib/feedparser.py](https://github.com/bendikro/deluge-yarss-plugin/blob/master/yarss2/lib/feedparser.py)

到目前为止，在torrent 客户端中，最受支持的feed格式是_RSS_（与Atom相反）和torrent内容的<tt class="docutils literal">附件</tt>标签。

### 外壳

附件标签必须将<tt class="docutils literal">type</tt>属性设置为“ application / x-bittorrent”，并且必须将torrent链接存储在<tt class="docutils literal">url</tt>属性中。它可能具有<tt class="docutils literal">length</tt>属性，该属性应指示.torrent文件的大小（以字节为单位）。

例：

<enclosure type =“ application / x-bittorrent” length =“ 12216” url =“ http://featuredcontent.utorrent.com/torrents/WillisEarlBeal-BitTorrent.torrent” />

### 媒体：内容

媒体内容标签实际上是名称空间<tt class="docutils literal">http://search.yahoo.com/mrss/</tt>下的“内容”标签。大多数bittorrent客户端不支持其通用形式的XML名称空间。大多数支持<tt class="docutils literal">media：content</tt>标签的客户端都假定该名称空间在Feed中称为<tt class="docutils literal">媒体</tt>，否则将无法识别该标签。

有关更多信息，请参见[媒体RSS规范](http://search.yahoo.com/mrss/)。

该<tt class="docutils literal">媒体内容::</tt>标签包括元数据属性。与bittorrent客户端相关的是 <tt class="docutils literal">url</tt>，它是torrent链接，而<tt class="docutils literal">filesize</tt>则是torrent内容的大小（以字节为单位）。

例：

<media：content url =“ http://featuredcontent.utorrent.com/torrents/WillisEarlBeal-BitTorrent.torrent” fileSize =“ 12216320” />

### 媒体：哈希

媒体哈希标签提供了已编码的洪流十六进制的信息哈希。

例：

<media：hash algo =“ sha1”> <8c056e06fbc16d2a2be79cefbf3e4ddc15396abe / media：hash>

### 链接

link标签包含torrent链接作为其主体。

例：

<link> http://featuredcontent.utorrent.com/torrents/WillisEarlBeal-BitTorrent.torrent </ link>

### 激流

torrent标签可以代替磁铁链接使用，也可以补充另一个带有torrent链接的标签。torrent标签仅提供两个属性，即<tt class="docutils literal">infohash</tt>和 <tt class="docutils literal">contentlength</tt>，这两个属性应该分别是torrent的十六进制编码的info-hash和torrent内容的大小。

尽管uTorrent不支持其他任何标签，<tt class="docutils literal">但</tt>该标签中通常会出现<tt class="docutils literal">Magneticuri</tt>和<tt class="docutils literal">文件名</tt>，分别包含磁力链接和Torrent名称

例：

<torrent>
        <infohash>“ 8c056e06fbc16d2a2be79cefbf3e4ddc15396abe </ infohash>
        <contentlength> 600162597 </ contentlength>
</ torrent>

有关更多信息，请参见[xmlns](http://xmlns.ezrss.it/0.1/)。

### 吉德

有时，torrent链接在RSS feed中被编码为GUID。

例：

<guid> http://featuredcontent.utorrent.com/torrents/WillisEarlBeal-BitTorrent.torrent </ guid>

但是，在大多数情况下，客户希望GUID只是该内容的唯一标识符，并且仅用于避免下载重复项。uTorrent是一个例外，因为它还会在guid标签中寻找种子链接。

### 结论

即使本节看起来像是对客户端的比较，但它的主要要点是，目前RSS提要中有许多表示洪流的方法，并且客户端支持某些而不支持其他。

从客户端支持中获得的主要好处是，非常需要这样的标准化文档，以使torrent RSS提要变得不像是妖术，并为torrent提要提供者提供明确的建议。

## Torrent RSS源

拟议的torrent 标准RSS提要格式是一种RSS 2.0提要，它使用<tt class="docutils literal">附件</tt>标记来显示种子内容。

该<tt class="docutils literal">TTL</tt>标签应得到支持和尊重。<tt class="docutils literal">ttl</tt>标记内的值的定义是客户端下次下次刷新Feed之前要等待的秒数。

所述<tt class="docutils literal">外壳</tt>标签必须包含一个<tt class="docutils literal">类型</tt>属性设置为<tt class="docutils literal">应用程序/ x-bittorrent的</tt> 和必须包含一个<tt class="docutils literal">URL</tt>包含洪流链接属性。

如果<tt class="docutils literal">附件</tt>标签符合上述规范，则应优先于RSS <tt class="docutils literal">项中</tt>找到的任何其他标签。

在<tt class="docutils literal">标题</tt>标签应该用于洪流的名称。

的<tt class="docutils literal">描述</tt>标签可以是用于内容的描述。如果<tt class="docutils literal">描述</tt>标签可用，则不应包含任何标记。它应该是纯文本。

客户经常需要仅通过检查<tt class="docutils literal">项目</tt>来确定洪流是否已经下载。因此，RSS提要应该包含一个<tt class="docutils literal">guid</tt>字段。如果可行的话，<tt class="docutils literal">guid</tt>应该是种子的信息哈希。这样，GUID将在不同的提要中匹配。

例：
```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
        <channel>
                <title> Featured content </title>
                <link> http://featuredcontent.utorrent.com/ </link>
                <item>
                        <title> WillisEarlBeal-BitTorrent </title>
                        <description>
                                The Principles of a Protagonist Bundle

                                Chicago native Willis Earl Beal came from humble musical beginnings- he
                                began as a street performer of sorts that was prone to leaving homemade
                                novels, artwork and CD-Rs across America to promote his work, suggesting
                                a desire to be heard. Thereafter, he relocated to Albuquerque, NM where
                                he continued his practice of 'gifting' as he simultaneously recorded a
                                set of songs on a discarded karaoke machine that would become Acousmatic
                                Sorcery, his Hot Charity/XL Recordings debut.
                        </description>
                        <guid> e380a6c5ae0fb15f296d29964a56250780b05ad7 </guid>
                        <enclosure
                                url="http://featuredcontent.utorrent.com/torrents/WillisEarlBeal-BitTorrent.torrent"
                                type="application/x-bittorrent" />
                </item>
        </channel>
</rss>
```

### 扩展的洪流属性

对于提供种子列表以及更详细的统计信息的种子网站，推荐的标签是[eztv](http://xmlns.ezrss.it/0.1/)定义的[标签](http://xmlns.ezrss.it/0.1/)。

例：

```xml
<torrent>
        <filename> WillisEarlBeal-BitTorrent </filename>
        <contentlength> 28571661 </contentlength>
        <magneturi> magnet:?xt=urn:btih:e380a6c5ae0fb15f296d29964a56250780b05ad7&dn=WillisEarlBean </magneturi>
        <trackers>
                <group order="ordered">
                        <tracker seeds="359" peers="3961">
                                udp://tracker.openbittorrent.com:80/announce
                        </tracker>
                </group>
                <group order="random">
                        <tracker seeds="365" peers="4451">
                                http://tracker.publicbt.com/announce
                        </tracker>
                        <tracker seeds="367" peers="4434">
                                udp://tracker.publicbt.com:80/announce
                        </tracker>
                        <tracker seeds="565" peers="6406">
                                udp://tracker.istole.it:80/announce
                        </tracker>
                        <tracker seeds="0" peers="0">
                                http://tracker.hexagon.cc:2710/announce
                        </tracker>
                </group>
        </trackers>
</torrent>

```