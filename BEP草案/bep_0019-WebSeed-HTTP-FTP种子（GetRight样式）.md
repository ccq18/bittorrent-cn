# WebSeed-HTTP / FTP种子（GetRight样式）

http://www.bittorrent.org/beps/bep_0019.html
 

## 抽象

使用HTTP或FTP服务器作为BitTorrent下载的种子。

## 基本原理

许多列出BitTorrent下载的网站还为同一文件提供HTTP或FTP URL。这些文件是相同的。WebSeeding BitTorrent客户端可以从任一来源下载，将所有部分放到一个完整的文件中。

HTTP或FTP服务器充当永久取消选择的种子。

## 优点

总有一个不为人知的种子，任何人都可以开始。

对于无法识别元数据添加的客户端，它不会破坏或更改任何内容。

不支持HTTP / FTP播种的客户端仍将从对等端共享原始来自HTTP / FTP服务器的片段中获得好处。

元数据不必更改。Download Manager工具（例如GetRight）通常可以通过单击网页上的多个链接并识别相同文件名的用户操作来为文件添加多个HTTP / FTP镜像URL。

每个人都非常熟悉HTTP / FTP服务器及其协议。

它已经在GetRight，Mainline客户端，uTorrent，Azureus，libTorrent和其他可能的版本中实现。

仅在BitTorrent客户端中需要更改。无需更改跟踪器，HTTP或FTP服务器。HTTP或FTP服务器上不需要脚本。

由于许多非常常见的客户端（尤其是Mainline客户端本身）已经支持此功能，因此可以完全使用公司或个人的现有HTTP / FTP服务器完成BitTorrent下载的种子。

## 元数据扩展

在元数据文件的主要区域中，而不是“ info”部分的一部分中，将有一个新的密钥“ url-list”。该密钥将引用一个或多个URL，并将包含可检索种子数据的网址列表。如果客户端无法使用此密钥，则可以安全地忽略该密钥。

<dt>例如（出于可读性考虑，在多行中）：</dt>

d 8：announce27：http：//tracker.com/announce 8：url-list26：http：//mirror.com/file.exe 4：info ...

如果“ URL列表” URL以斜杠结尾，则“ /”客户端必须从种子文件中添加“名称”以构成完整的URL。这样，.torrent生成器就可以对单个文件和多文件torrent将该字段视为相同。

### 多文件洪流

BitTorrent客户端通常使用torrent信息部分中的“名称”创建一个文件夹，然后使用该文件夹中的info部分中的“ path / file”项。对于多文件洪流，“ URL列表”必须是一个根文件夹，客户端可以在其中添加相同的“名称”和“路径/文件”以创建请求的URL。

<dt>例如：</dt>

... 8：URL列表22：http：//mirror.com/pub/ 4：infod5：filesld6：lengthi949e4：pathl10：Readme.txte e4：name7：michael

客户将使用所有这些来构建URL：[http](http://mirror.com/pub/michael/Readme.txt) : [//mirror.com/pub/michael/Readme.txt](http://mirror.com/pub/michael/Readme.txt)

## 客户实施概述

客户端应忽略url列表中不知道的任何协议。客户端可以选择实现HTTP，但不能选择FTP，反之亦然。

HTTP / FTP是“流”类型的协议，并且没有BitTorrent的块概念。对于HTTP，您可以使用字节范围在任何地方恢复或下载您指定的特定范围，但是对于FTP，您只能说出从何处开始下载。

我想在从BitTorrent对等体下载的数据中包含许多顺序块（“间隙”），因此HTTP / FTP连接将有很大的空间可填充。您可以使用HTTP的字节范围来请求各个块-但每个块请求将显示在服务器的日志中，如果他们的日志中显示来自同一IP的100个连接，则有人会认为这是对他们的拒绝服务攻击。

在GetRight的实现中，我对通常的“稀有优先”样片选择方法进行了一些更改，以更好地允许在样片之间形成“间隙”。这样，文件中就有更长的空间可用于填充HTTP和FTP线程。他们可以从间隔的开头开始下载，直到结束。

## 客户实施说明

更改了标准BitTorrent算法，以优化HTTP和FTP连接填充文件中许多顺序块的能力。

### 间隙的定义

间隙是客户端连续没有的多个零件的空间。

给定一个位域“ YYnnnnYnnY”，其中Y是它拥有的片段，n是它没有的片段，存在两个“间隙”，一个是4个片段，另一个是2。

### 作品选择

主要变化是作品选择。

如果其他所有东西都差不多，那么从BitTorrent对等方请求片段时最好从2的间隔中选择一个片段。

在任何间隙中，最好从末尾开始填写（即，首先从最高件数开始）。

因此给定位域“ YYnnnnYnnY”，如果所有n个块的稀有度都相似，则最好选择＃个块“ YYnnnnY ### Y”之一，最好是选择块$“ YYnnnnYn $ Y”

这些最大化了HTTP / FTP连接的连续部分。这样一来，HTTP / FTP连接就可以从一个很大的间隙开始，并且可以在下载到客户端已经拥有的数据之前下载最多的数据。

### 更改样片选择

将“稀有优先”片段选择更改为“与另一完整片段有最大距离的罕见”。

#### 极少出现最大差距

扫描最稀有零件时，如果与另一个完整零件的距离小于当前最稀有零件的距离，则该距离必须为“ rare-X”。或者，如果距离大于当前片段的距离，则稀疏+ X可以选作下一个片段。（没有比在时间和规模上似乎有意义的更好的理由，X是对等点数减去1的平方根。）

因此，如果3个对等方拥有当前最稀有的棋子，则正常算法会选择2个对等方拥有的棋子。更改后的算法将要求只有一个对等方才能拥有该作品，如果该作品与完整作品的距离小于当前最稀有作品的差距。

如果间隙更大，并且棋子是相同的“稀有度”或通常的“ rare-1”，则选择该棋子。（因此，如果差距更大，则将选择一个有2个或3个同伴的作品。）

因此，给定“ YYnnn1Yn2Y”，除非1比2稀有得多，否则最好选择2号。

伪代码逻辑：
```
X = sqrt(Peers) - 1;
Gap = 0;
CurGap = 0;
CurRarest = MaxPieces+1;
for (i=0; i<MaxPieces; i++) {
    if (IDoNotHavePiece(i)) {
        Gap++;
        if (PeerHasPiece(i)) {
            PieceRareness = NumberOfPeersWithThePiece();
            if (PieceRareness<(CurRarest-X) ||
                (PieceRareness<=(CurRarest+X) && Gap>CurGap)) {
                CurRarest = PieceRareness;
                CurGap = Gap;
                NextPiece = i;
            }
        }
    } else {
        Gap = 0;
    }
}
```

#### 填补差距

如果文件的完成率超过50％，它将随机使用不同的方法进行乐曲选择。（拥有超过50％的资源，您应该拥有大量其他同行想要下载的作品。）

每隔几件（在GetRight中，随机数为十分之一），它将从完整的件中选择间隙最小的件，而忽略所有稀有性。对于位域“ YYnnnnYnnY”，它将选择片段“ YYYYnnYn＃Y”。这有助于填补小的空白。

客户可以选择是否执行此步骤，以及实施是否可以使用文件完成的其他百分比。

伪代码逻辑：

```
Gap = 0;
Piece = -1;
CurGap = MaxPieces+1;
for (i=0; i<MaxPieces; i++) {
    if (IDoNotHavePiece(i)) {
        Gap++;
        if (PeerHasPiece(i)) {
            Piece = i;
        }
    } else {----
        if (Gap<CurGap && Gap>0 && Piece!=-1) {
            CurGap = Gap;
            NextPiece = Piece;
        }
        Gap = 0;
        Piece = -1;
    }
}
```

### HTTP和FTP优化

无需更改HTTP / FTP协议或服务器。

如果客户端知道HTTP / FTP下载是BitTorrent下载的一部分，则在建立第一个连接时，最好在文件中的某个位置随机启动HTTP / FTP下载。这样，它获得的第一个HTTP片段很有可能对与BitTorrent对等方共享很有用。

如果在启动HTTP / FTP连接时已经在进行BitTorrent下载，则HTTP / FTP应该从最大间隔的开头开始。给定一个位域“ YYnnnnYnnY”，它应该从＃开始：“ YY＃nnnYnnY”

如果它成功地从HTTP / FTP服务器下载了一个片段，但是SHA校验和不匹配，则必须关闭连接，并且该URL应该被丢弃。

如果客户端收到“忙”答复，则无需丢弃HTTP或FTP服务器URL。

## 多文件洪流

使用HTTP / FTP服务器处理多文件种子时，将需要其他选择算法。

客户端可以选择BitTorrent片段进行优化，以便可以从HTTP / FTP服务器下载整个大文件。

对于包含小文件的种子，一件可能需要几次HTTP / FTP传输。在这种情况下，使用BitTorrent进行操作可能更有意义。例如，如果有100个1KB文件，即使在最坏的情况下，假设32KB个文件，也要进行100次HTTP / FTP传输才能完成文件，但是只有4个BitTorrent文件请求。

为较小的文件赋予BitTorrent片段选择较高的优先级，为较大的文件赋予HTTP / FTP较高的优先级将很好地工作。

## 另一个可能的客户实施

如果客户端仅支持HTTP而不支持FTP，则可以利用HTTP的字节范围请求，但一次请求多个。

片段块可以视为对HTTP服务器的单个集合和单个字节范围的请求。这将减少HTTP连接的数量，并且可能对客户端有效。

可以将碎片视为10、50或100的块。如果我这样做，我可能会选择“每块碎片”为MaxPieces / 20。因此，一次请求大约5％的文件。

## 不推荐的客户端实现

客户端可以简单地使用HTTP字节范围来请求各个片段。

一些服务器管理员不希望这样，因为单个文件的日志中将有100或1000个请求。有些人甚至认为这是对他们的拒绝服务攻击。

## 有关其他协议的更多信息

HTTP和FTP在此BEP中列为种子协议，但是客户端可以使用允许下载数据的**任何**其他协议。HTTPS，FTPS或SFTP是显而易见的，但是许多客户端不太可能支持（GetRight可以执行HTTPS和FTPS，但不能执行SFTP）。

我确信RTSP和MMS也可以。甚至可以使用Usenet的NNTP协议。

其他协议可能会有其他问题，例如不允许下载从文件开头以外的任何地方开始。

客户端可以选择仅实现HTTP或FTP协议之一，而不能同时实现。