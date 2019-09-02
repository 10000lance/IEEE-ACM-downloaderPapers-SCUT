## 构建会议的基础信息（xml文档）

### 例如https://dblp.org/db/conf/date/



### 一、 打开https://dblp.org/db/conf/date/

![图片](./img/1.jpg)

### 二、获取该页面下每个年份的xml文档地址

![](./img/2.jpg)

<center>遍历每个年份的xml文档，例如打开https://dblp.org/rec/xml/conf/date/2019asd.xml</center>

![](./img/3.jpg)

### 三、将https://dblp.org/与url标签内的相对地址拼接成完整url，并进入该页面，即为会议内每个年份的论文收录的首页面

![](./img/4.jpg)

### 四、找到该页面下收录了所有论文基础信息的xml文档地址并进入

![](./img/5.jpg)

<center>例如https://dblp.org/search/publ/api?q=toc%3Adb/conf/date/asd2019.bht%3A&h=1000&format=xml</center>

<center>每个hit标签内就是一篇论文的基础信息（作者，title，年份，论文收录地址）</center>

![](./img/6.jpg)



## 对于一个年份内有多个volume的情况，需另作处理

<center>例如https://dblp.org/db/conf/date/date2004.html<center>

![](./img/7.jpg)

### 前三步骤一样，从第四步开始

### 四、获取每个volume的地址并进入

![](./img/11.jpg)

![](./img/8.jpg)

### 五、需要一个一个抓取论文的xml文档，再拼接到一起

![](./img/9.jpg)

![](./img/10.jpg)

