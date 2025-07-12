# AGENTS.md 
## 技術介紹
1. 這個是使用python2.7 和python3.8兼容打造的semi通信
2. acsbridge_KHCP是代表HOST端口
3. tsc代表的是equipment端
4. 目前使用的是SEMI E82通訊
5. secsgem目錄是acsbridge_KHCP和tsc 所使用用的secsgem套件
6. 目前e82_callback 只能收到解析後的S6F11(Event Reports Send)成json格式
    - 但是不知道目前流程運作，希望你可以進行分析

## 想要的的功能
1. 希望e82_callback可以收到解析後的S5F1 (Alarm Report Send)



## 規定
1. 回复內容要使用繁體中文
2. 在python知道print或log 英文
3. 在python 只能使用print({}.format) log也是
