规范
Isap是一种基于海绵的认证加密方案，使用n位排列P。Isap实例由安全参数k进行参数化，该参数定义k位的加密安全级别，并指定密钥、标记和nonce的大小。实例由(sh, sb, se, sk)进一步参数化，它指定对排列P进行评估的轮数。我们将产生的排列表示为ph、pb、pe和pk。此外，它由两个速率值rh和rb参数化。速率rh将用于未键控海绵和键控海绵中不太可能进行多次评估的状态，这意味着它可能相当大，因为泄漏将受到限制。速率rb将用于键控海绵中可能被评估多次的状态，这意味着我们必须通过限制对该状态进行评估的总次数来限制泄漏量。在Isap的每个成员中，我们设置rh = n - 2k和rb = 1。排列P的Isap族成员的整数参数为sh, sb, se, sk，速率为rh, rb，安全参数为k


Isap可以被看作是一种先加密后mac的设计，使用相同的k位密钥进行加密和消息认证。表2.1总结了Isap规范中使用的参数和符号。
表2.1: Isap接口和模式的符号
K,N,T
M,C,A
⊥	密钥K，现在是N，标签T，所有K = 128位
明文M，密文C，关联数据A(以rh-bit块M表示)iCi,一个i）
错误，验证验证过的密文失败
|x| 
x||y
x⊕y
S = Sr ||Sc
X=[x]k || [x]k	以位为单位的位串x的长度
位串x和y的连接
位串x和y的Xor

n位海绵态S，外层r位Sr 和c位的内部部分Sc
位串x分成前k位dxek (MSB)和最后k位 [x]k(LSB)
	

加密是通过在流模式下使用键控海绵结构来执行的，显著的区别是，首先调用IsapRk来生成子键KE∗．IsapEnc得到一个K -bit密钥K，一个K -bit nonce N和一个任意大的消息M作为输入，生成一个大小为|M|的密文C。该函数在算法3和图2.1d中描述。它首先使用标志f = ENC调用IsapRk进行加密，以选择初始值IVKE和z = n - k，从而派生出一个(n - k)位的子密钥KE∗．一旦这个子键生成，使用置换pE的常规基于海绵的流模式将在高速率rH下进行评估。IsapEnc是流模式，解密与M、C交换的角色相同。
身份验证与IsapMac
对于消息身份验证，我们使用一个基于海绵的散列函数来构建一个后缀mac。IsapMac得到一个K位的密钥K，一个K位的nonce N，任意大的关联数据a和任意大的密文C，并输出一个大小为K位的标记T。该函数在算法5中进行了描述，如图2.1e所示。它首先初始化状态为N k IVa，并使用具有高速率rh的排列ph以普通海绵模式吸收非秘密输入(A, C)。请注意，A和C之间的域分离是使用状态内部位“1”的异或来执行的。然后将产生的状态S分割为k位值dSek 和(n−k)位bScn−k．内镜下动态慢动作影像的价值k 作为输入字符串提供给IsapRk以生成一个子键Ka∗，最后调用输入Ka的排列ph值∗ k平衡计分卡n−k 得到k位标签T。
为了验证，标签T0 以同样的方式从接收到的nonce N、关联数据A和密文C重新计算，并与接收到的标签T进行比较。
1.算法1 E(K, N, A, M)
输入:密钥K∈{0,1}K, nonce N∈{0,1}k，关联数据A∈{0,1}∗，明文M∈{0,1}∗
输出: C∈{0,1}|M|， tag T∈{0,1}k
加密C←IsapEnc(K, N, M)
认证T←IsapMac(K, N, A, C)返回C, T
2.算法2 D(K, N, A, C, T)
输入:密钥K∈{0,1}K，
nonce N∈{0,1}k，关联数据A∈{0,1}∗，密文C∈{0,1}∗， tag T∈{0,1}k
输出: 明文M∈{0,1}∗，或差错;
验证T0 ←IsapMac(K, N, A, C)
如果t6 = T0是⊥
M←IsapEnc(K, N, C)返回M
3.算法3 IsapEnc(K, N, M)
输入:密钥K∈{0,1}K, nonce N∈{0,1}k，消息M∈{0,1}∗
输出: C∈{0,1}|M|
初始化
M1. . . Mt ← rh-bit blocks of M k 0−|M| mod rh Ke∗ ← IsapRk(K, enc, N)
S ← Ke∗ k N
Squeese
for i=1.....t do
S←pE(S)
Ci←Srh⊕Mi
C←[C1||.......||Ct][M]
返回C
4.算法4 IsapRk(K, f, Y)
输入:密钥K∈{0,1}K，


输出: 会话密钥K∗ ∈{0,1}z
5.算法5 IsapMac(K, N, A, C)
输入:密钥K∈{0,1}K, nonce N∈{0,1}k，关联数据A∈{0,1}∗，

输出:tag T∈{0,1}k

推荐参数

表2.2总结了Isap的推荐参数集。成员Isap-A-128a和Isap-K-128a，其中A和K表示底层密码排列，为快速实现指定了一个参数选择。我们还在Isap-A-128和Isap-K-128中指定了一个更保守的参数选择。推荐的参数(表2.2)按顺序排列，从主要建议开始，然后是第二个、第三个和第四个。我们记得sh, sb, se, sk表示排列的轮数ph, pb, pe, pk。
表2.2: Isap的推荐配置
Name	Permutation	Security level	Bit size of			Rounds	
		k	n	rh	rb	sh	sb	se	sk
Isap-A-128a
Isap-K-128a
Isap-A-128
Isap-K-128	Ascon-p
Keccak-p[400]
Ascon-p
Keccak-p[400]	128
128
128
128	320
400
320
400	64
144
64
144	1
1
1
1	12
16
12
20	1
1
12
12	6
8
12
12	12
8
12
12
初始值IVa、IVka、IVke分别作为不同算法的分域值，如表2.3所示。它们被定义为实例的所有相关参数的连接的8位整数值，加上一个用于每个IV的角色的常量。然后用0填充初始值，直到它们达到所需的n - k位长度。Isap-A-128和Isap-A-128a的iv长度为192位，而Isap-K-128和Isap-K-128a的iv长度为272位。
表2.3:十六进制Isap实例的初始值
Isap-P -rshh,r,sbb,se,sk -k	IVa IVka IVke	1 k k k r h k r b k s h k s b k s e k s k k 0∗ 2 k k k r h k r b k s h k s b k s e k s k k 0∗ 3 k k k r h k r b k s h k s b k s e k s k k 0∗
Isap-A-128a	IVa IVka IVke	01 80 4001 0C01060C 00* 02 80 4001 0C01060C 00* 03 80 4001 0C01060C 00*
Isap-K-128a	IVa IVka IVke	01 80 9001 10010808 00* 02 80 9001 10010808 00* 03 80 9001 10010808 00*
Isap-A-128	IVa IVka IVke	01 80 4001 0C0C0C0C 00* 02 80 4001 0C0C0C0C 00* 03 80 4001 0C0C0C0C 00*
Isap-K-128	IVa IVka IVke	01 80 9001 140C0C0C 00* 02 80 9001 140C0C0C 00* 03 80 9001 140C0C0C 00*
安全要求
所有Isap家族成员都提供128位安全性，以防止加密攻击，这是基于非基于的认证加密与相关数据(AEAD)的概念:它们保护明文(长度除外)的机密性和包括相关数据(在自适应伪造尝试下)的密文的完整性。参见表3.1。请注意，与往常一样，一个小的常数因子的安全性损失是预期的。
表3.1: Isap推荐参数配置的安全声明
要求		Security in bits		
	Isap-A-128a	Isap-K-128a Isap-A-128	Isap-K-128
保密的明文
完整的明文
关联数据的完整性
现时标志完整性	128
128
128
128	128
128
128
128	128
128
128
128	128
128
128
128

所有算法的设计都是为了实现实际的安全性，防止通过被动侧信道攻击恢复秘密主密钥，假设实现对简单的功率分析(SPA)包括模板攻击是安全的。
认证加密解密程序
1.认证加密E(K, N, A, M)
输入:密钥K∈{0,1}K, nonce N∈{0,1}k，关联数据A∈{0,1}∗，明文M∈{0,1}∗
输出: C∈{0,1}|M|， tag T∈{0,1}k
加密：
KE*=g1(N,K)
C=ENCN,KE*(M)
身份验证:
Y=H(N,A,C)
KA*=g2(Y,K)
T=MACKA*(Y)
返回值（C，T）
2.认证解密D(K, N, A, C, T)
输入:	key K∈{0,1}k，
nonce N∈{0,1}k，
关联数据A∈{0,1}∗，
C∈{0,1}∗，
tag T∈{0,1}k
输出: 明文M∈{0,1}|C|，或差错;
Verification
Y = H(N, A, C)
Ka∗ = g2(Y, K)
T0 = MACKa∗ (Y)
if T 6= T0 return ⊥
Decryption
Ke∗ = g1(N, K)
M = DECN,Ke∗ (C)
return M

