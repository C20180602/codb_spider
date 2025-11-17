# codb_spider
CyanoOmicsDB spider, using KEGG id to get gene ID, Uniprot ID and GO annotations.

# environment
playwright==1.55.0

playwright install chromium 

pandas==2.3.3

numpy==2.3.5

openpyxl==3.1.5

# method
因为这个网站是VUE架构的，内容都需要动态访问，直接request不太行，所以选择用playwright访问+解析

但实现方式非常笨拙，每次都要重新启动playwright的浏览器，访问完了又关闭，很呆

用selenium应该也可以，不过会比playwright麻烦很多，更重量级一些