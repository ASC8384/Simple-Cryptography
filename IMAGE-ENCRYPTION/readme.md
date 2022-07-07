&emsp;&emsp;首先读取一张照片，将图像的灰度值存入$img$中，若为彩色图像则转换为灰度图像，并显示灰度图像。利用$size()$函数将图片$img$的长和宽赋值给$h，w$。本算法通过多次置乱和扩散操作对图像进行加密。

## 一、置乱

&emsp;&emsp;此算法先将图片随机分成k个垂直矩形，所以要生成k个和为h的伪随机数列 $n_1,n_2...n_k$ ,令$q_i= \frac{h}{n_i}$，$N_i=n_1+...+n_i$。令原像素位置为$（x,y）$,对于$N_{i-1} < x < N_i$，通过

\left\{\begin{matrix}
 x = {q_i(x-N_i)+y　mod　q_i}\\
y = \frac{y-y　mod　q_i}{q_i}+N_i
\end{matrix}\right.
对图像像素位置进行置乱操作。

## 二、扩散

&emsp;&emsp;采用Logistic映射扩散，是一种可产生的非线性系统。自定义一个密钥列表$key$，大小为7，其中$key[1]-key[3]$为混沌初始条件$x_i∈[0，1]$，$key[4]-key[6]$为分叉函数$μ_i∈(3.569945...，4]$，$（1 ≤ i ≤ 3）$。定义$r_1,r_2,r_3$表示的是混沌序列值与255的乘积。

每一次加密时

&emsp;&emsp;计算混沌值

 $$x_i =μ_i * x_i * (1-x_i)$$

$$r_i=int(x*255)$$

通过公式&emsp;$imgn(x,y)=((r_1+r_2) \bigoplus r_3+img(x,y))　mod　256$  改变置乱后的像素灰度值实现扩散，其中$img(x,y)$为置乱后$(x,y)$处的像素灰度值，$imgn(x,y)$为通过Logistic映射扩散后的灰度值。  
<br/><br/>
循环上述两步操作，对图像实现加密。

<br/><br/>

## 摘要
&emsp;&emsp;我们分析了 Fridrich的混沌图像加密算法，证明了该算法的代数弱点使它容易受到选择密文攻击。我们提出了一种攻击，揭示了秘密排列，用于洗牌像素的一个圆形输入。通过实例和仿真结果证明了该攻击的有效性。我们还表明，我们所提出的攻击可以推广到其他著名的混沌图像加密算法。

&emsp;&emsp;在过去的25年里，对混沌映射的复杂动力学和加密系统进行了全面的研究。1989年，通过迭代混沌位置置换和值置换算法设计了Fridrich的混沌图像加密方案，在混沌密码学领域得到了广泛关注。2010年，Solak等人提出了一种利用密像素之间的影响网络对弗里德里奇方案进行选择密文攻击。本文在其创造性工作的基础上，用简明的数学语言详细研究了弗里德里奇方案的一些性质。然后，给出了索拉克攻击方法的实际性能上的一些小缺陷。这项工作为进一步优化对弗里德里奇的方案及其变体的攻击提供了一些基础。
<br/><br/>


## 参考文献
[1] Solak E , ?OKAL, CAHIT,  Yildiz O T , et al. CRYPTANALYSIS OF FRIDRICH'S CHAOTIC IMAGE ENCRYPTION[J]. International Journal of Bifurcation & Chaos, 2010, 20(5):1405-1413.

[2]Eric Xie Yong, Chengqing Li , et al. On the cryptanalysis of Fridrich's chaotic image encryption scheme[J]. Signal Processing, 2017.
<br/><br/>

# 效果

<div align=center><img src="https://i.ibb.co/fnZ69Ky/2.png" height=300></div>
<div align=center>原图</div>
<br/><br/>
<div align=center><img src="https://i.ibb.co/SV85Y8K/3.png" height=300></div>
<div align=center>加密后图片</div>
