uTorrent传输协议(uTP) 

http://www.bittorrent.org/beps/bep_0029.html

 

## 基本原理

uTP的动机是让BitTorrent客户端不中断互联网连接，同时仍可充分利用未使用的带宽。

问题在于，DSL和电缆调制解调器通常具有一个与其最大发送速率不成比例的发送缓冲区，该缓冲区可以容纳几秒钟的数据包。BitTorrent流量通常是后台传输，并且比检查电子邮件，电话和浏览Web优先级低，但是当使用常规TCP连接时，BitTorrent会迅速填满发送缓冲区，给所有交互式流量增加几秒钟的延迟。

当与其他服务争夺带宽时，BitTorrent使用多个TCP连接的事实为其带来了不公平的优势，这夸大了BitTorrent填充上传管道的影响。这样做的原因是因为TCP在连接之间平均分配可用带宽，并且一个应用程序使用的连接越多，它获得的带宽份额就越大。

解决此问题的传统方法是将BitTorrent客户端的上传速率限制为上行链路容量的80％。80％的人为交互流量留有余地。

该解决方案的主要缺点是：

1.  用户需要配置他的BitTorrent客户端，否则将无法立即使用。
2.  用户需要知道他的互联网连接的上传容量。此容量可能会发生变化，尤其是在可能连接到大量不同网络的笔记本电脑上。
3.  20％的余量是任意的，会浪费带宽。每当没有互动流量与BitTorrent竞争时，就会浪费掉额外的20％。只要有相互竞争的交互式流量，它就不能使用超过20％的容量。

uTP通过使用调制解调器队列大小作为其发送速率的控制器来解决此问题。当队列过大时，它会回退。

这样，在没有竞争的情况下，它可以利用全部上传的容量，并且在有很多互动流量时，它可以使几乎没有任何内容减速。

## 概要

本文档假定您对基于TCP和基于窗口的拥塞控制的工作原理有所了解。

uTP是一种传输协议，位于UDP之上。因此，它必须（并有能力）实施自己的拥塞控制。

与TCP相比的主要区别是基于延迟的拥塞控制。请参阅[拥塞控制](http://www.bittorrent.org/beps/bep_0029.html#congestion-control)部分。

与TCP一样，uTP使用基于窗口的拥塞控制。每个插座具有<tt class="docutils literal">max_window</tt>其确定的字节插座可以具有最大数目_的飞行中_在任何给定的时间。任何已发送但尚未确认的数据包都在进行中。

<tt class="docutils literal">传输中</tt>的字节数为<tt class="docutils literal">cur_window</tt>。

套接字只能在<tt class="docutils literal">cur_window</tt> + <tt class="docutils literal">packet_size</tt> 小于或等于min（<tt class="docutils literal">max_window</tt>，<tt class="docutils literal">wnd_size</tt>）的情况下发送数据包。数据包大小可能有所不同，请参见[数据包大小](http://www.bittorrent.org/beps/bep_0029.html#packet-sizes)部分。

<tt class="docutils literal">wnd_size</tt>是从另一端发布的窗口。它为运行中的数据包数设置了上限。

如果<tt class="docutils literal">max_window</tt> 小于数据包大小，则实现可能违反上述规则，并且对数据包进行步调，以使平均<tt class="docutils literal">cur_window</tt>小于或等于<tt class="docutils literal">max_window</tt>。

每个套接字都保留一个状态，以用于来自另一个端点（<tt class="docutils literal">Reply_micro</tt>）的最后一次延迟测量。每当接收到数据包时，都会通过 从主机当前时间中减去<tt class="docutils literal">timestamp_microseconds</tt>（以微秒为单位）来更新此状态（请参见[标头格式](http://www.bittorrent.org/beps/bep_0029.html#header-format)）。

每次发送数据包时，套接字的<tt class="docutils literal">reply_micro</tt>值都会放入数据包头的<tt class="docutils literal">timestamp_difference_microseconds</tt>字段中。

与TCP不同，uTP中的序列号和ACK是指数据包，而不是字节。这意味着uTP 在重新发送数据时无法_重新打包_数据。

每个套接字保留发送数据包<tt class="docutils literal">seq_nr</tt>时要使用的下一个序列号的状态。它还保留最后收到的序列号<tt class="docutils literal">ack_nr的状态</tt>。最早的未确认数据包是<tt class="docutils literal">seq_nr</tt> - <tt class="docutils literal">cur_window</tt>。

## 标头格式

版本1标头：

```
0       4       8               16              24              32
+-------+-------+---------------+---------------+---------------+
| type  | ver   | extension     | connection_id                 |
+-------+-------+---------------+---------------+---------------+
| timestamp_microseconds                                        |
+---------------+---------------+---------------+---------------+
| timestamp_difference_microseconds                             |
+---------------+---------------+---------------+---------------+
| wnd_size                                                      |
+---------------+---------------+---------------+---------------+
| seq_nr                        | ack_nr                        |
+---------------+---------------+---------------+---------------+
```

所有字段均按网络字节顺序（大端）。

### version

这是协议版本。当前版本是1。

### connection_id

这是一个随机的，唯一的编号，用于标识属于同一连接的所有数据包。每个套接字具有一个用于发送数据包的连接ID和一个用于接收数据包的不同连接ID。启动连接的端点确定要使用的ID，并且返回路径具有相同的ID + 1。

### timestamp_microseconds

这是发送此数据包的时间戳的“微秒”部分。使用posix上的gettimeofday（）和Windows上的QueryPerformanceTimer（）进行设置。此时间戳的分辨率越高，效果越好。设置与实际发送时间越接近越好。

### timestamp_difference_microseconds

这是本地时间与最后一个接收到的数据包中的时间（接收到最后一个数据包的时间）之间的时差。这是从远程对等点到本地计算机的链路的最新单向延迟度量。

当新打开一个套接字并且还没有任何延迟采样时，必须将其设置为0。

### wnd_size

广告接收窗口。这是32位宽，以字节为单位指定。

窗口大小是当前正在传输的字节数，即已发送但未确认的字节数。如果接收端已满，则公告的接收窗口允许另一端限制窗口大小，如果该接收端无法更快地接收。

发送数据包时，应将其设置为套接字的接收缓冲区中剩余的字节数。

### 延期

扩展头链接列表中的第一个扩展的类型。0表示没有扩展名。

当前有一个扩展名：

1.  选择性的袜子

扩展是链接的，就像TCP选项一样。如果扩展字段不为零，则uTP标头后面紧跟两个字节：

```
0               8               16
+---------------+---------------+
| extension     | len           |
+---------------+---------------+
```

其中<tt class="docutils literal">extension</tt>指定链接列表中下一个扩展的类型，0终止列表。而<tt class="docutils literal">len个</tt>指定这个扩展的字节数。只需前进<tt class="docutils literal">len个字节</tt>，即可跳过未知的扩展名。

#### 选择性确认

选择性ACK是一种扩展，可以无序地选择性地对数据包进行ACK。它的有效载荷是至少32位的位掩码，是32位的倍数。每一位代表发送窗口中的一个数据包。发送窗口之外的位将被忽略。设置位指定已接收到数据包，清除位指定未接收到数据包。标头看起来像这样：

```
0               8               16
+---------------+---------------+---------------+---------------+
| extension     | len           | bitmask
+---------------+---------------+---------------+---------------+
                                |
+---------------+---------------+
```

请注意，扩展名的len字段指的是字节，在此扩展名中必须至少为4，并且为4的倍数。

仅当在接收的流中跳过至少一个序列号时，才发送选择性ACK。因此，掩码中的第一位表示ack_nr +2。假定发送此数据包时ack_nr + 1已被丢弃或丢失。设置的位表示已收到的数据包，清除的位表示尚未收到的数据包。

位掩码具有相反的字节顺序。第一个字节以相反的顺序表示数据包[ack_nr + 2，ack_nr + 2 + 7]。字节中的最低有效位表示ack_nr + 2，字节中的最高有效位表示ack_nr + 2 +7。掩码中的下一个字节以相反的顺序表示[ack_nr + 2 + 8，ack_nr + 2 + 15]，等等。位掩码不限于32位，而可以是任何大小。

这是一个位掩码的布局，它表示在选择性ACK位字段中表示的前32个数据包确认：

```
0               8               16
+---------------+---------------+---------------+---------------+
| 9 8 ...   3 2 | 17   ...   10 | 25   ...   18 | 33   ...   26 |
+---------------+---------------+---------------+---------------+
```

图中的数字将位掩码中的位映射到要添加到<tt class="docutils literal">ack_nr</tt>的偏移量 ，以便计算该位正在确认的序列号。

### 类型

类型字段描述数据包的类型。

它可以是以下之一：

<dt>ST_DATA = 0</dt>

常规数据包。套接字处于连接状态，并且有要发送的数据。ST_DATA数据包始终具有数据有效负载。

<dt>ST_FIN = 1</dt>

完成连接。这是最后一个数据包。它关闭连接，类似于TCP FIN标志。此连接的序列号永远不会大于此数据包中的序列号。套接字将此序列号记录为<tt class="docutils literal">eof_pkt</tt>。这使套接字可以等待仍可能丢失的数据包，甚至在收到ST_FIN数据包后也无法按顺序到达。

<dt>ST_STATE = 2</dt>

状态包。用于发送无数据的ACK。不包含任何有效负载的数据包不会增加<tt class="docutils literal">seq_nr</tt>。

<dt>ST_RESET = 3</dt>

强制终止连接。类似于TCP RST标志。远程主机对此连接没有任何状态。它已过时，应终止。

<dt>ST_SYN = 4</dt>

连接SYN。与TCP SYN标志类似，此数据包启动连接。序列号初始化为1。连接ID初始化为随机数。syn数据包是特殊的，在此连接上发送的所有后续数据包（ST_SYN的重新发送除外）均以连接ID + 1发送。连接ID是另一端预期在其响应中使用的连接ID。

收到ST_SYN时，应使用数据包头中的ID初始化新套接字。套接字的发送ID应该初始化为ID +1。返回通道的序列号初始化为随机数。另一端期望有一个ST_STATE数据包（仅ACK）作为响应。

### seq_nr

这是此数据包的序列号。与TCP相反，uTP序列号不是指字节，而是包。序列号告诉另一端应按什么顺序将数据包送回应用程序层。

### ack_nr

这是在另一个方向上最后接收到的数据包发送者的序列号。

## 连接设置

这是说明启动连接的交换和状态的图。c。*指套接字本身中的状态，pkt。*指数据包头中的字段。

```
initiating endpoint                           accepting endpoint

          | c.state = CS_SYN_SENT                         |
          | c.seq_nr = 1                                  |
          | c.conn_id_recv = rand()                       |
          | c.conn_id_send = c.conn_id_recv + 1           |
          |                                               |
          |                                               |
          | ST_SYN                                        |
          |   seq_nr=c.seq_nr++                           |
          |   ack_nr=*                                    |
          |   conn_id=c.rcv_conn_id                       |
          | >-------------------------------------------> |
          |             c.receive_conn_id = pkt.conn_id+1 |
          |             c.send_conn_id = pkt.conn_id      |
          |             c.seq_nr = rand()                 |
          |             c.ack_nr = pkt.seq_nr             |
          |             c.state = CS_SYN_RECV             |
          |                                               |
          |                                               |
          |                                               |
          |                                               |
          |                     ST_STATE                  |
          |                       seq_nr=c.seq_nr++       |
          |                       ack_nr=c.ack_nr         |
          |                       conn_id=c.send_conn_id  |
          | <------------------------------------------<  |
          | c.state = CS_CONNECTED                        |
          | c.ack_nr = pkt.seq_nr                         |
          |                                               |
          |                                               |
          |                                               |
          | ST_DATA                                       |
          |   seq_nr=c.seq_nr++                           |
          |   ack_nr=c.ack_nr                             |
          |   conn_id=c.conn_id_send                      |
          | >-------------------------------------------> |
          |                        c.ack_nr = pkt.seq_nr  |
          |                        c.state = CS_CONNECTED |
          |                                               |
          |                                               | connection established
     .. ..|.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..|.. ..
          |                                               |
          |                     ST_DATA                   |
          |                       seq_nr=c.seq_nr++       |
          |                       ack_nr=c.ack_nr         |
          |                       conn_id=c.send_conn_id  |
          | <------------------------------------------<  |
          | c.ack_nr = pkt.seq_nr                         |
          |                                               |
          |                                               |
          V                                               V
```

连接由其<tt class="docutils literal">conn_id</tt>标头标识。如果新连接的连接ID与现有连接冲突，则连接尝试将失败，因为ST_SYN数据包将在现有流中意外出现并被忽略。

## 数据包丢失

如果<tt class="docutils literal">尚未</tt><tt class="docutils literal">确认</tt>具有序号（<tt class="docutils literal">seq_nr</tt> - <tt class="docutils literal">cur_window</tt>）的数据包（这是发送缓冲区中最旧的数据包，并且预期将确认下一个数据包），但是已经通过它（通过选择性ACK）确认了3个或更多数据包），则认为该数据包已丢失。类似地，当接收到3个重复的<tt class="docutils literal">ack</tt>时，假定<tt class="docutils literal">ack_nr</tt> + 1丢失（如果已发送具有该序列号的数据包）。

这也适用于选择性的码头。在选择性ack消息中确认的每个数据包都计为一个重复的ack，如果重复3个或更多，则应触发重新发送至少有3个数据包之后的数据包。

当数据包丢失时，将<tt class="docutils literal">max_window</tt>乘以0.5以模拟TCP。

## 超时时间

通过落入范围（last_ack_nr，ack_nr]或通过选择性ACK消息明确确认而被确认的每个数据包都应用于更新<tt class="docutils literal">rtt</tt>（往返时间）和<tt class="docutils literal">rtt_var</tt>（rtt方差）测量。是当前数据包之前在套接字上收到的最后一个ack_nr，而ack_nr是当前接收的数据包中的字段。

该<tt class="docutils literal">RTT</tt>和<tt class="docutils literal">rtt_var</tt>只更新已发送一次数据包。这避免了弄清楚哪个包被确认，第一个或第二个包的问题。

<tt class="docutils literal">每次ACK</tt>数据包时，<tt class="docutils literal">rtt</tt>和<tt class="docutils literal">rtt_var</tt>均通过以下公式计算：

增量= rtt-packet_rtt 
rtt_var + =（abs（delta）-rtt_var）/ 4; 
rtt + =（packet_rtt-rtt）/ 8;

每次<tt class="docutils literal">rtt</tt>和<tt class="docutils literal">rtt_var</tt>更新时，与套接字关联的数据包的默认超时也会 更新。设置为：

超时= max（rtt + rtt_var * 4，500）;

其中以毫秒为单位指定超时。即，数据包的最小超时为1/2秒。

套接字每次发送或接收数据包时，都会更新其超时计数器。如果在最后一次超时计数器重置后的毫秒数内没有数据包到达<tt class="docutils literal">超时</tt>，套接字将触发超时。它将其<tt class="docutils literal">packet_size</tt> 和<tt class="docutils literal">max_window</tt>设置为最小的数据包大小（150字节）。这允许它再发送一个数据包，如果窗口大小减小到零，这就是套接字重新启动的方式。

初始超时设置为1000毫秒，然后根据上面的公式进行更新。对于每个超时的连续后续数据包，超时都会加倍。

## 包大小

为了尽可能减少对慢速拥塞链路的影响，uTP将其数据包大小调整为每个数据包最小150字节。使用较小的数据包的好处是不会阻塞慢速的上行链路，并具有较长的序列化延迟。使用这么小的数据包的代价是，数据包头的开销变得很大。在高速率下，使用大数据包大小；在低速率下，使用小数据包大小。

## 拥塞控制

uTP拥塞控制的总体目标是使用单向缓冲区延迟作为主要的拥塞度量，以及像TCP这样的数据包丢失。关键是要避免在发送数据时以完整的发送缓冲区运行。对于DSL / Cable调制解调器来说，这是一个特别的问题，在DSL / Cable调制解调器中，调制解调器中的发送缓冲区经常有几秒钟的数据空间。uTP（或任何后台流量协议）的理想缓冲区利用率是在0字节缓冲区利用率下运行。也就是说，任何其他流量都可以在任何时间发送，而不会被后台流量阻塞发送缓冲区所阻塞。实际上，uTP目标延迟设置为100毫秒。每个套接字的目标是在发送链接上永远不会看到超过100毫秒的延迟。如果是这样，它将回退。

这有效地使uTP屈服于任何TCP流量。

这是通过在通过uTP发送的每个数据包中包含一个高分辨率时间戳来实现的，并且接收端计算其自己的高分辨率计时器与其接收的数据包中的时间戳之间的差。然后将此差异反馈到数据包的原始发送方（timestamp_difference_microseconds）。该值作为绝对值没有意义。机器中的时钟极有可能不同步，尤其是未达到微秒级的分辨率，并且数据包传输的时间也包括在这些时间戳的差异中。但是，该值与以前的值相比很有用。

每个插槽在最近两分钟内保持最小值的滑动最小值。此值称为_base_delay_，用作基线，即主机之间的最小延迟。从每个数据包的时间戳差异中减去base_delay时，您可以得到套接字上当前缓冲延迟的度量。此度量称为_our_delay_。它有很多噪音，但用作驱动程序来确定是增大还是减小发送窗口（控制发送速率）。

该_CCONTROL_TARGET_是缓冲延迟的UTP接受上行链路上。当前，延迟目标设置为100 ms。_off_target_是实际测量的延迟与目标延迟之间的距离（根据CCONTROL_TARGET-our_delay计算）。

套接字结构中的窗口大小指定了我们在连接中可能总共有（未确认）运行中的字节数。发送速率直接与此窗口大小相关。飞行中的字节越多，发送速率越快。在代码中，窗口大小称为 <tt class="docutils literal">max_window</tt>。它的大小大致由以下表达式控制：

delay_factor = off_target / CCONTROL_TARGET; 
window_factor = excellent_packet / max_window; 
scaled_gain = MAX_CWND_INCREASE_PACKETS_PER_RTT * delay_factor * window_factor;

第一个因子将_off_target_缩放为目标延迟的单位。

然后将scaled_gain添加到max_window中：

max_window + = scaled_gain;

如果off_target大于0，则将使窗口变小；如果off target小于0，则将使窗口变大。

如果max_window小于0，则将其设置为0。窗口大小为零表示套接字可能不发送任何数据包。在这种状态下，套接字将触发超时，并将窗口大小强制为一个数据包大小，然后发送一个数据包。有关更多信息，请参见超时部分。