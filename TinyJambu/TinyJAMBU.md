# TinyJAMBU算法
## TinyJAMBU中使用的运算、变量和函数定义如下：
### 运算符
1.$\oplus$:按位异或  
2.&:按位与  
3.$\lnot$:取反  
4.$\lfloor a \rfloor$:对a取整
### 变量和常量
1.$a_{i…j}$:由$a_i$,$a_{i+1}$,…,$a_j$组成  
2.$AD$:相关数据  
3.$ad_i$:第i个相关数据位  
4.$adlen$:以位为单位的相关数据的长度  
5.$C$:密文  
6.$c_i$:第i个密文位  
$FrameBits$:三位帧位  
$FrameBits$值为1，即[0,0,1]表示nonce  
$FrameBits$值为3，即[0,1,1]表示相关数据  
$FrameBits$值为5，即[1,0,1]表示明文和密文  
$FrameBits$值为7，即[1,1,1]用于最终确定   
7.$K$:表示密钥  
8.$k_i$:第i位密钥  
9.$klen$:密钥的位长度     
10.$M$:明文  
11.$m_i$:明文的位长度  
12.$NONCE$:96位的随机数值(nonce)  
13.$nonce_i$:第i位nonce  
14.$P_n$:n轮的128位置换  
15.$s_i$:第i位的置换状态  
16.$T$:64位的认证标签  
17.$t_i$:第i位的认证标签  
## 状态更新(The Keyed Permutation $P_n$)
在TinyJAMBU中，使用128位Keyed Permutation。$P_n$由n轮组成。在第i轮置换中，使用128位非线性反馈移位寄存器更新状态，如下所示： 

公式：  
     　
StateUpdate(S, K,i):  
$feedback = s_0 \oplus s_{47} \oplus (\lnot (s_{70} ＆ s_{85})) \oplus s_{91} \oplus k_{i　mod　klen}$  
$for　j　from　0 to　126: s_j = s_{j+1}$  
$s_{127} = feedback $  
end  
解释：这个状态更新函数通过将状态$S$的$s_0$，$s_{47}$，$s_{91}$，$s_{70}$与$s_{85}$的与运算，以及$k_{i　mod　klen}$这5个值进行异或，从而得到feeedback，然后让$S$的0-126位与其各自的前面一位相等，而最后的$s_{127}$则等于feeedback，从而实现了状态$S$的更新。

代码:
```
#The Keyed Permutation P_n: 状态更新函数
def state_update(S, K, i_round): #P_n由i_round轮组成。在第i轮置换中，使用128位非线性反馈移位寄存器更新状态
    for i in range(i_round):
        feedback = S[0] ^ S[47] ^ (0x1 - (S[70] & S[85])) ^ S[91] ^ (K[(i_round % klen)]) 
        for j in range(127):
            S.insert(j, S.pop()+1)
            # print(S) 
        S[127] = feedback
    return S

#128-bit key
#96-bit nonce
#64-bit tag
#128-bit state
klen = 128
S = [0x0]*128
K = [0x0]*128

a = state_update(S, K, 2048)
```
## 初始化（The initialization）
在TinyJAMBU-128的Keyed Permutation中，使用TinyJAMBU-128的128位密钥，klen设置为128。TinyJAMBU-128的初始化包括两个阶段：密钥设置(key setup)和随机数值设置(nonce setup)。
### 密钥设置(key setup)：
密钥设置是使用keyed permutation P_1024对状态进行随机化。其流程为：  
(1)设$S$为0  
(2) 使用$p_{1024}$更新状态  

代码:
```
    S = [0]*128
    .......
    ## The initialization 初始化
    # Key setup： 使用keyed permutation P_1024对状态S进行随机化
    S = perm.state_update(S, K, 1024)
```
### 随机数值设置(nonce setup):
Nonce setup由三个步骤组成。在每个步骤中，nonce的帧位（$FrameBits$值为1）与状态$S$异或，然后我们使用keyed permutation $P_{640}$更新状态，然后nonce的32位与状态$S$异或。  

公式：  
$for　i　from　0　to　2: $  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
$s_{96...127}=s_{96...127} \oplus nonce_{32i...32i+31}$  
end for

代码:
```
 # Nonce setup：由三个步骤组成。在每个步骤中，nonce的帧位（FB_n）与状态$S$异或，然后我们使用keyed permutation P_640更新状态，然后nonce的32位与状态$S$异或  
    for i in range (3):
        a = 0
        b = 0
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_n))
        S = perm.state_update(S, K, 640)
        a = 0
        b = 0
        S[96:128] = list(a ^ b for a, b in zip(S[96:128], N[32*i:32*i+32]))
```
## 处理相关数据
初始化后，我们处理相关数据$AD$。在每个步骤中，相关数据的帧位($FrameBits$值为3)与状态$S$异或，然后我们使用keyed permutation $P_{640}$更新状态，然后相关数据的32位与状态$S$异或。  

### 处理完整的关联数据块公式:  
$for　i　from　0　to　\lfloor adlen/32 \rfloor$:  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{640}$  
$s_{96...127}=s_{96...127} \oplus ad_{32i...32i+31}$  
end for


代码：
```
## Processing the associated data 处理相关数据
    #处理完整的关联数据块：每个步骤中，相关数据的帧位（FB_ad）与状态S异或，然后我们使用keyed permutation P_640更新状态，最后相关数据AD的32位与状态S异或。
    if adlen>=32: #每次处理32位
        for j in range (int(adlen/32)):
            a = 0
            b = 0
            S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_ad))
            S = perm.state_update(S, K, 640)
            a = 0
            b = 0
            S[96:128] = list(a ^ b for a, b in zip(S[96:128], AD[32*j:32*j+32]))
```

### 处理剩余部分的关联数据块：  
如果最后一个块不是完整块（称为部分块），则最后一个块与状态$S$异或，部分块中关联数据的字节数与状态$S$异或。  
公式：  
$if(adlen　mod　32)>0$  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{640}$  
$lenp = adlen mod 32 　$/*　部分块中的位数　*/  
$startp = adlen-lenp$ 　/*　部分块中的起始位置 */  
$s_{96...96+lenp-1}=s_{96...96+lenp-1} \oplus ad_{startp...adlen-1}$  
/* 部分块中的字节数与状态异或　*/  
$s_{32...33}=s_{32...33} \oplus (lenp/8) $   
end if

代码：
```
#处理剩余部分的关联数据块：如果最后一个块不是完整块（称为部分块），则最后一个块与状态S异或，部分块中关联数据的字节数与状态S异或。
    if adlen%32 >0:
        a = 0
        b = 0
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_ad))
        S = perm.state_update(S, K, 640) #与处理完整的相关数据一致
        a = 0
        b = 0
        lenp=adlen%32 #部分块中的位数
        startp=adlen-lenp #部分块的起始位置
        S[96:96+lenp] = list(a ^ b for a, b in zip(S[96:96+lenp], AD[startp:adlen]))  #相关数据最后一部分块AD（startp...adlen）与状态S(96...96+lenp)异或
        S[32]^=lenp #最后一个部分块的长度（字节）与状态S异或
```
## 加密(The encryption)
在处理相关数据后，我们对明文$M$进行加密。在每一步中，明文的帧位（$FrameBits$值为为5）与状态$S$异或，然后我们使用keyed permutation $P_{1024}$更新状态，然后明文的32位与状态$S$异或，我们通过将明文与状态的另一部分异或获得32位密文。  

### 处理明文的完整块公式：  
$for　i　from　0　to　\lfloor mlen/32 \rfloor$:  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{1024}$  
$s_{96...127}=s_{96...127} \oplus m_{32i...32i+31}$  
$c_{32i...32i+31}=s_{64...95} \oplus m_{32i...32i+31}$  
end for  


代码：
```
#处理完整的明文块
    if mlen>=32: 
        for k in range (int(mlen/32)): #每次处理32位
            a = 0
            b = 0
            S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_pc)) #明文的帧位(FB_pc)与状态S异或
            S = perm.state_update(S, K, 1024) #使用keyed permutation P_1024更新状态S
            a = 0
            b = 0
            S[96:128] = list(a ^ b for a, b in zip(S[96:128], M[32*k:32*k+32])) #明文M的32位与状态S异或
            a = 0
            b = 0
            C[32*k:32*k+32] = list(a ^ b for a, b in zip(S[64:96], M[32*k:32*k+32])) #明文M与状态S的另一部分进行异或来获得32位密文
```

### 处理剩余部分的明文块：
如果最后一个块不是完整块（称为部分块），则最后一个块与状态$S$异或，部分块中关联数据的字节数与状态$S$异或。

公式：  
if($mlen$ mod 32)>0  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{1024}$  
$lenp = mlen　mod　32 $　/*　部分块中的位数　*/  
$startp = mlen-lenp$ 　/*　部分块中的起始位置　*/  
$s_{96...96+lenp-1}=s_{96...96+lenp-1} \oplus m_{startp...adlen-1}$  
$c_{startp...mlen-1}=s_{64...64+lenp-1} \oplus m_{startp...mlen-1}$  
/* 最后一个部分块的长度（字节）与状态异或　*/  
$s_{32...33}=s_{32...33} \oplus (lenp/8) $   
end if  

代码：
```
 #处理剩余部分的明文块：如果最后一个块不是完整块（它是部分块），则最后一个块与状态S异或，部分块中的字节数与状态S异或。
    if mlen%32 >0: 
        a = 0
        b = 0
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_pc)) 
        S = perm.state_update(S, K, 640) #与处理完整的明文块一致
        a = 0
        b = 0
        lenp=mlen%32 #部分块中的位数
        startp=mlen-lenp #部分块的起始位置
        S[96:96+lenp] = list(a ^ b for a, b in zip(S[96:96+lenp], M[startp:mlen])) #明文最后一部分块M（startp...mlen）与状态S(96...96+lenp)异或
        C[startp:mlen] = list(a ^ b for a, b in zip(S[64:64+lenp], M[startp:mlen]))  #明文最后一部分块M(startp...clen)与状态S(64...64+lenp)异或,得到最后一部分密文
        S[32]^=lenp #最后一个部分块的长度（字节）与状态S异或
```
## 终止(The finalization)
加密明文后，我们生成64位认证标签$T$，如下所示。终止的帧位（$FrameBits$值为7）与状态$S$异或。  
公式:  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{1024}$  
$t_{0...31}=s_{64...95}$  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{640}$  
$t_{0...31}=s_{64...95}$  
## 解密(The decryption)
在解密过程中，相关数据的初始化和处理与加密过程相同。在处理相关数据后，我们解密密文$C$。在每一步中，明文的帧位（$FrameBits$值为5）与状态$S$异或，然后我们使用keyed permutation $P_{1024}$更新状态。我们将密文与32个状态位$s_{64...95}$进行异或运算，得到32位明文，然后将明文与状态位$s_{96··127}$进行异或运算。 

### 处理完整的密文块公式：  
$for　i　from　0　to　\lfloor mlen/32 \rfloor$:  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{1024}$  
$m_{32i...32i+31}=s_{64...95} \oplus c_{32i...32i+31}$  
$s_{96...127}=s_{96...127} \oplus m_{32i...32i+31}$  
end for  
  
代码：
```
    #处理完整的密文块：
    if clen>=32:
        for k in range (int(clen/32)): #每次处理32位
            a = 0
            b = 0
            S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_pc)) #明文的帧位(FB_pc)与状态S异或
            S = perm.state_update(S, K, 1024)
            a = 0
            b = 0
            S[96:128] = list(a ^ b for a, b in zip(S[96:128], C[32*k:32*k+32])) #密文C与状态S_(96··128)的32位进行异或运算更新状态S
            a = 0
            b = 0
            M[32*k:32*k+32] = list(a ^ b for a, b in zip(S[64:96], C[32*k:32*k+32])) #密文C与状态S_(64··96)进行异或运算得到明文M
            # print((C))
        # print(S)
```
### 处理剩余部分的密文块:  
如果最后一个块不是完整块（它是部分块），则部分块中的字节数与状态$S$异或。  
公式：  
$if(mlen　mod　32)>0 $   
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$   
Update the state using $P_{1024}$  
$lenp = mlen$ mod 32 　/*　部分块中的位数　*/  
$startp = mlen$-$lenp$ 　/*　部分块中的起始位置　*/  
$m_{startp...mlen-1}=s_{64...64+lenp-1} \oplus c_{startp...adlen-1}$  
$s_{96...96+lenp-1}=s_{96...96+lenp-1} \oplus m_{startp...mlen-1}$  
/* 最后一个部分块的长度（字节）与状态异或　*/  
$s_{32...33}=s_{32...33} \oplus (*lenp*/8)$  
end if 

代码:
```
    #处理剩余部分的密文块：如果最后一个块不是完整块（它是部分块），则最后一个块与状态S异或，部分块中的字节数与状态S异或。
    if clen%32 >0:
        a = 0
        b = 0
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_pc)) 
        S = perm.state_update(S, K, 640) #与处理完整的密文块一致
        a = 0
        b = 0
        lenp=clen%32 #部分块中的位数
        startp=clen-lenp #部分块的起始位置
        S[96:96+lenp] = list(a ^ b for a, b in zip(S[96:96+lenp], C[startp:clen])) #密文最后一部分块C（startp...clen）与状态S(96...96+lenp)异或
        M[startp:clen] = list(a ^ b for a, b in zip(S[64:64+lenp], C[startp:clen]))  #密文最后一部分块C(startp...clen)与状态S(64...64+lenp)异或,得到最后一部分明文
        S[32]^=lenp #最后一个部分块的长度（字节）与状态S异或
```
## 验证(The verification)
在解密明文之后，我们生成一个64位认证标签$T'$，然后将$T'$与接收到的标签$T$进行比较。最终确定的帧位$FrameBits$的值为7。 

公式：  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{1024}$  
$t'_{0...31}=s_{64...95}$  
$s_{36...38}=s_{36...38} \oplus FrameBits_{0...2}$  
Update the state using $P_{640}$  
$t'_{32...63}=s_{64...95}$  
如果$T'$=$T$，则接受消息;否则，拒绝消息。  
