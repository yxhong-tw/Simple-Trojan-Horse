# Simple-Trojan-Horse
 
## 簡要介紹
> 這是一個簡單的木馬病毒實作。\n
> 雖然沒有實作傳播與將本體寫入開機自啟動區塊的功能，但目前版本能透過 Socket 自 Server 傳送 ==Shell Command== 至對 Client (被感染裝置) ，從而達到控制別人的電腦~~做壞壞的事~~之目的。
> 使用情境為假設目標裝置為 Windows 10 以上之 x64 作業系統、有連上網路，下載了本專案的 Client 檔案並執行。

## 支持功能
- 支持 Server 以 Shell Command 控制被感染裝置
- 支持多個 Client 同時連線至 Server
- 支持單命令控制指定 Client
- 支持單命令控制所有 Client
- 支持 Client 斷線重連

## 支援命令
- `server stop` : 關閉 Server、假性關閉 Client
- `list clients` : 列出目前所有已連線的 Client
- `client [Clinet Index] stop` : 假性關閉編號為 `[Client Index]` 的 Client
- `client [Client Index] stop by user` : 真性關閉編號為 `[Client Index]` 的 Client
- `client [Client Index] [Shell Command]` : 使編號為 `[Client Index]` 的 Client 執行 `[Shell Command]`
- `client all [Command]`: 使全部的 Client 都執行 `[Command]`
> 假性關閉: 不會關閉程式，會在冷卻時間後嘗試重新連線。
> 真性關閉: 關閉程式，不會再嘗試重新連線。
> `[Command]` = `stop` + `stop by user` + `[Shell Command]`
> `[Shell Command]` 請參考[這裡](https://docs.microsoft.com/zh-tw/windows-server/administration/windows-commands/windows-commands)。

## 運行要求
- Windows 10 以上之 x64 作業系統
- 裝置有連上網路

## 詳細說明
### Server
#### Module
```python
import socket
import time
import threading
```
Server 利用以上三個 module 實作。

#### Class
```python
class ServerThread(threading.Thread)
class ClientThread(threading.Thread)
class SendCommandToAllClientThread(threading.Thread)
```
Server 內共有三個多線程的類別。
詳細內容於下面內容，此處不贅述。

#### Main Function
##### 流程說明
- 主 Thread
    1. 定義 Server IP, Port
       不贅述。
    2. 建立 Server Socket
       使用 Server Ip 與 Port 建立 Server Socket。
       若建立失敗，會嘗試重新建立，超過三次仍失敗便報錯並停止程式。
    3. 建立 ServerThread
       建立 ServerThread，用於處理 accept 新 Client 之任務。
       若建立失敗，會嘗試重新建立，超過三次仍失敗便報錯並停止程式。
    4. 接收輸入的命令、檢查命令語法
       接收 Server 使用者輸入的命令並分析語法
        - 收到 `all` 命令。
          開啟 SendCommandToAllClientThread，用於處理傳送命令給所有 Client 之任務。
          結束傳送後關閉 SendCommandToAllClientThread，回到 4.，接收輸入命令、檢查命令語法。
        - 收到一般命令
          對指定 Client 傳送命令後，回到 4.，接收輸入命令、檢查命令語法。
        - 收到 `server stop` 命令。
          對所有 Client 發送 `stop` 命令，接著關閉 Server Socket，等待 ServerThread 關閉，結束程式。
        - 收到語法錯誤命令
          印出命令語法錯誤訊息，回到 4.，接收輸入命令、檢查命令語法。
          
- ServerThread
    1. 檢查 Server Socket 目前狀態
       如果 Server Socket 已關閉，便等待所有 ClientThread 關閉，再結束此線程。
       如果 Server Socket 正常開啟，便執行下一步。
    2. Accept 新 Client 的連線
       成功 Accept 的話，就建立 ClientThread，用於接收 Client 回傳之資料。
       若建立 ClientThread 失敗，會嘗試重新建立，超過三次仍失敗便報錯並停止程式。
    3. 回到 1.，檢查 Server Socket 目前狀態。

- ClientThread
    1. 檢查 Server Socket 與 Client Socket 目前狀態。
       如果 Server Socket 已關閉，就關閉 Client Socket 並結束此線程。
       如果 Client Socket 已關閉，就結束此線程。
       如果皆正常開啟，就執行下一步。
    2. 接收 Client 回傳的資料。
       若接收失敗，會嘗試重新接收，超過三次仍失敗就關閉此 Client Socket 與此線程。
    3. 如果接收到 `client stop`，便關閉此 Client Socket 與此線程。
       否則印出回傳的資料。
    4. 回到 1.，檢查 Server Socket 與 Client Socket 目前狀態。

- SendCommandToAllClientThread
    1. 傳送 `all` 至 Client，使 Client 進入執行命令後不會回傳結果之模式。
       若傳送失敗，會嘗試重新傳送，超過三次仍失敗，就關閉此線程。
    2. 傳送命令至 Client，使 Client 執行相應動作。
       若傳送失敗，會嘗試重新傳送，超過三次仍失敗，就關閉此線程。
    3. 完成所有任務，關閉此線程。

### Client
#### Module
```python
import socket
import subprocess
import ctypes
import os
import time
from posixpath import commonpath
```
Client 利用以上六個 module 實作。

#### Function
```python
def HideWindows()
def SetAutoRunScript()
def ConnectToServer()
```
Client 內共有三個函式。
其中 HideWindows() 與 SetAutoRunScript() 尚在開發中，因此本次報告不說明。
ConnectToServer() 的詳細說明則於下方，此處不贅述。

#### 流程說明
- 主程式
    1. 定義 Server IP、Port 與其他**運行所需的變數**
       - userClose : 如果收到 `stop by user` 命令，此值將為 True；否則為 False。
       - allCommand : 如果收到 `all` 命令，此值將為 True；否則為 False。
    2. 檢查 userClose
       如果 userClose 為 True，代表 Server 傳送了 `stop by user` 命令，結束程式。
       如果 userClose 為 False，則繼續下一步。
    3. 建立 clientSocket 並連線至 Server。
    4. 若成功連線，接收 Server 傳送之 Client 編號，並回傳成功連線訊息。
    5. 接收來自 Server 的命令。
       如果接收失敗，會嘗試重新建立，超過三次仍失敗便報錯並關閉 clientSocket。　等待冷卻時間後，回到 2.，檢查 userClose，重新啟動 Client。
    6. 若接收到的命令為 `all`
        - 將 allCommand 設為 True，再接收一次命令
        - 反之設為 False
    8. 收到命令
        - 如果收到的命令為 `stop`
          傳送 `client stop` 至 Server，接著關閉 clientSocket，等待冷卻時間後，回到 2.，檢查 userClose，重新啟動 Client。
        - 如果收到的命令為 `stop by user`
          將 userClose 設為 true，傳送 `client stop` 至 Server，接著關閉 clientSocket，等待冷卻時間後，回到 2.，檢查 userClose。
        - 若為一般的 `[Shell Command]`，則進入下一步。
    9. 將命令透過 `subprocess.Popen()` 執行，並透過 `.communicate()` 得到輸出結果。
    10. 檢查 allCommand
        - 若 allCommand 為 False，執行命令後不回傳結果至 Server。
        - 若 allCommand 為 True，執行命令後回傳結果至 Server。
          如果傳送失敗，會嘗試重新傳送，若超過三次仍失敗，則關閉 clientSocket，等待冷卻時間後，回到 2.，檢查 userClose，重新啟動 Client。

- ConnectToServer()
    1. 宣告 clientSocket
    2. clientSocket 嘗試連線至 Server
        - 連線成功，回傳 clientSocket
        - 連線失敗，再嘗試連線一次
