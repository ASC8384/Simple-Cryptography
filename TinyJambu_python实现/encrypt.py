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
#12位状态 S，128位密钥 K，96位nonce N，64位认证标签 T，输入的明文 M
#明文长度 mlen，32位相关数据 AD，相关数据长度 adlen
S = [0]*128
K = [0]*128
N = [0]*96
T = [0]*64
M = 'It is a place where kindly affections exist among allthe members of the family. The parents take goodcare of their children,and the children are interestedin the activities of their parents'
mlen=len(M)
# C = [0]*32
C=[]
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
#对明文进行处理 32位
M=list(M)
M=[ord(i) for i in M]


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
    if adlen>=32:
        for j in range (int(adlen/32)): #每次处理32位
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
        S[36:39] = list(a ^ b for a, b in zip(S[36:39], FB_ad)) #相关数据的帧位（FB_ad）与状态S异或
        S = perm.state_update(S, K, 640) #与处理完整的相关数据一致
        a = 0
        b = 0
        lenp=adlen%32 #部分块中的位数
        startp=adlen-lenp #部分块的起始位置
        S[96:96+lenp] = list(a ^ b for a, b in zip(S[96:96+lenp], AD[startp:adlen]))  #相关数据最后一部分块AD（startp...adlen）与状态S(96...96+lenp)异或
        S[32]^=lenp #最后一个部分块的长度（字节）与状态S异或

    ## The encryption 加密
    #在对明文M进行加密的每一步中，明文的帧位(FB_pc)与状态S异或，然后我们使用keyed permutation P_1024更新状态，然后明文M的32位与状态S异或，就可以通过将明文M与状态S的另一部分进行异或来获得32位密文
    
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
    return C

c = tinyjambu(S, K, N, T, M, C, AD, FB_n, FB_ad, FB_pc, FB_f) #求密文C
print(c)
