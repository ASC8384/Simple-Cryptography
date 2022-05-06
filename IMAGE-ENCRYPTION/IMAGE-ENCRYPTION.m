clear all;
close all;
clc;

img=imread('lenna2.jpg');%读取图片，相对路径
mysize=size(img);%当只有一个输出参数时，返回一个行向量，该行向量的第一个元素时矩阵的行数，第二个元素是矩阵的列数。
if numel(mysize)>2%如果是彩色图像
   img=rgb2gray(img); %将彩色图像转换为灰度图像
   fprintf("图像为彩色图");
end
imshow(img,[])
[h,w]=size(img);
if h>w
    img = imresize(img, [w w]);
    fprintf("图像长宽不一样，图像可能失真");
end
if h<w
    img = imresize(img, [h h]);  
    fprintf("图像长宽不一样,图像可能失真");
end
k=20;%产生k个伪随机数

[h,w]=size(img);
all=h;%一列的长度
n=zeros(1,k);
n=randperm(all-1,k-1);
n(k)=all;
n=sort(n);%和为all，长度为k的伪随机序列
N1=zeros(1,k);
for i=1:k
    if i==1
        N1(i)=n(i);
        continue;
    end
    N1(i)=n(i)-n(i-1);
end
n=sort(N1);
q=zeros(1,k);
for i=1:k
    q(i)=all/n(i);
end
N=zeros(1,k+1);
for i=1:k+1
    if i==1
        N(i)=1;
        continue;
    end
    N(i)=N(i-1)+n(i-1);%N(i)=n(0)+n(1)+...+n(i);
end
%置乱与复原的共同参数,就相当于密码，有了这几个参数，图片就可以复原


pp=10;%迭代次数
key=[0.343,0.432,0.63,3.769,3.82,3.85,1];%logistic扩散参数(自定义),3.5699456...<u<=4,序列成混沌
x1=key(1);
x2=key(2);
x3=key(3);%x(n+1)=u*x(n)(1-xn),x1,x2,x3为x(0)

u1=key(4);
u2=key(5);
u3=key(6);%%x(n+1)=u*x(n)(1-xn)，u1,u2,u3为u
%选择虫口-logistic模型
%pixel'(i,j)=((r1+r2)^r3)+pixel(i,j)%256)
%r1,r2,r3为x1(n)*255,x2(n)*255,x3(n)*255


index=1;
for i=1:pp
    index=1;
    imgn=zeros(h,w);
    for y=1:h
        if y>=N(index+1)
            index=index+1;
        end
        for x=1:w
            x1=u1*x1*(1-x1);
            x2=u2*x2*(1-x2);
            x3=u3*x3*(1-x3);
            %混沌值位于[0,1]区间内，所以可以看做是一个系数，乘以最大灰度值并转成整数用于异或运算即可
            r1=fix(x1*255);
            r2=fix(x2*255);
            r3=fix(x3*255);
            yy=(q(index)*(y-N(index))+mod(x,q(index))+1);
            yy=fix(yy);
            xx=((x-mod(x,q(index)))/q(index)+N(index)+1);
            xx=fix(xx);
            imgn(yy,xx)=mod((bitxor((r1+r2),r3)+img(y,x)),256);
        end
        x1=key(1);
        x2=key(2);
        x3=key(3);
    end
    img=imgn;
end
%置乱操作
imgn = uint8(imgn);

figure
imshow(img,[])%治乱后的图片
imwrite(imgn,'zhiluan.jpg');
