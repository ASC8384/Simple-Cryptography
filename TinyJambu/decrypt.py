'''#!/usr/bin/env python'''
# coding: utf-8
import tinyjambu_perm as perm
"""
TinyJAMBU Hafif Blok Şifreleyicisinin Python ile Gerçeklenmesi
Orijinal makaleye
https://csrc.nist.gov/CSRC/media/Projects/lightweight-cryptography/documents/finalist-round/updated-spec-doc/tinyjambu-spec-final.pdf
adresinden ulaşabilirsiniz.
"""

## klen = 128
## other lengths and starting values are below
#12位状态 S，128位密钥 K，96位nonce N，64位认证标签 T，输入的密文 C
#密文长度 clen，32位相关数据 AD，相关数据长度 adlen
S = [0]*128
K = [0]*128
N = [0]*96
T = [0]*64
#M = [0]*32
M=[]
C = [4681, 4724, 4640, 4713, 4723, 4640, 4705, 4640, 4720, 4716, 4705, 4707, 4709, 4640, 4727, 4712, 4709, 4722, 4709, 4640, 4715, 4713, 4718, 4708, 4716, 4729, 4640, 4705, 4710, 4710, 4709, 4707, 5748, 5737, 5743, 5742, 5747, 5664, 5733, 5752, 5737, 5747, 5748, 5664, 5729, 5741, 5743, 5742, 5735, 5664, 5729, 5740, 5740, 5748, 5736, 5733, 5664, 5741, 5733, 5741, 5730, 5733, 5746, 5747, 6688, 6767, 6758, 6688, 6772, 6760, 6757, 6688, 6758, 6753, 6765, 6761, 6764, 6777, 6702, 6688, 6740, 6760, 6757, 6688, 6768, 6753, 6770, 6757, 6766, 6772, 6771, 6688, 6772, 6753, 6763, 6757, 7712, 7783, 7791, 7791, 7780, 7779, 7777, 7794, 7781, 7712, 7791, 7782, 7712, 7796, 7784, 7781, 7785, 7794, 7712, 7779, 7784, 7785, 7788, 7780, 7794, 7781, 7790, 7724, 7777, 7790, 7780, 7712, 8820, 8808, 8805, 8736, 8803, 8808, 8809, 8812, 8804, 8818, 8805, 8814, 8736, 8801, 8818, 8805, 8736, 8809, 8814, 8820, 8805, 8818, 8805, 8819, 8820, 8805, 8804, 8809, 8814, 8736, 8820, 8808, 9445, 9376, 9441, 9443, 9460, 9449, 9462, 9449, 9460, 9449, 9445, 9459, 9376, 9455, 9446, 9376, 9460, 9448, 9445, 9449, 9458, 9376, 9456, 9441, 9458, 9445, 9454, 9460, 9459]
clen=len(C)
AD= [0]*32
adlen=32

#FrameBits：三位帧位。
# TB_n 帧值为1，表示 nonce
#TB_ad 帧值为3，表示 相关数据
#TB_pc 帧值为5，表示 明文与密文
#TB_f 帧值为7，表示 终止
FB_n = [0,0,1]
FB_ad= [0,1,1]
FB_pc= [1,0,1]
FB_f = [1,1,1]
def tinyjambu(S, K, N, T, M, C, AD, FB_n, FB_ad, FB_pc, FB_f):
    ## The initialization 初始化
    # Key setup： 使用keyed permutation P_1024对状态S进行随机化
    S = perm.state_update(S, K, 1024)

    # Nonce setup：由三个步骤组成。在每个步骤中，nonce的帧位（FB_n）与状态S异或，然后我们使用keyed permutation P_640更新状态，然后nonce的32位与状态异或
    for i in range (3):
        a = 0
        b = 0
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_n))
        S = perm.state_update(S, K, 640)
        a = 0
        b = 0
        S[96:128] = list(a ^ b for a, b in zip(S[96:128], N[32*i:32*i+32]))


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

    ## The decryption 解密
    #在解密密文C的每一步中，明文的帧位(FB_pc)与状态S异或，然后我们使用keyed permutation P_1024更新状态。我们先将密文C与状态S_(96··128)的32位进行异或运算更新状态S，然后将密文C与状态S_(64··96)进行异或运算得到明文M。
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
    return M

m = tinyjambu(S, K, N, T, M, C, AD, FB_n, FB_ad, FB_pc, FB_f)
m=''.join([chr(i) for i in m]);
print(m)
