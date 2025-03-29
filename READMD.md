# Web Search Agent

Web Search Agent 是一個 infra tool，能夠針對指定的標題文字進行網路搜尋，並返回相關的網頁結果。這個工具可以幫助使用者/開發者快速獲取關於特定主題的網路資訊，整合成結構化的 JSON 格式數據。

## 功能介紹

- 根據輸入的標題或查詢詞進行網路搜尋
- 返回相關的搜尋結果，包含網頁標題、URL、內容摘要等資訊
- 對搜尋結果進行相關度評分
- 支援多個初始查詢以獲取更全面的搜尋結果
- 輸出結構化的 JSON 格式，方便後續處理和分析

## 輸出格式說明

工具輸出的 JSON 檔案包含以下主要欄位：

- `title`: 搜尋的主標題
- `initial_queries`: 用於搜尋的初始查詢列表
  - `query`: 查詢字串
- `initial_responses`: 每個初始查詢的搜尋結果
  - `query`: 查詢字串
  - `results`: 搜尋結果列表
    - `title`: 網頁標題
    - `url`: 網頁網址
    - `content`: 內容簡短摘要
    - `raw_content`: 完整的內容摘要（如果可用）
    - `score`: 相關度評分 (0-1 之間的數值，越高表示越相關)
- `sections`: 根據搜尋結果產生的主題分區列表
  - `title`: 分區標題
  - `description`: 分區描述
  - `search_queries`: 針對此分區生成的搜尋查詢列表
    - `query`: 查詢字串
  - `search_responses`: 此分區的搜尋結果列表
    - `query`: 查詢字串
    - `results`: 搜尋結果列表
      - `title`: 網頁標題
      - `url`: 網頁網址
      - `content`: 內容簡短摘要
      - `raw_content`: 完整的內容摘要（如果可用）
      - `score`: 相關度評分

## 輸出範例

以下是簡化版的輸出範例(詳細的輸出請查閱 /test/output/家寧和 Andy 之間的糾紛.json)：

```json
{
  "title": "家寧和 Andy 之間的糾紛",
  "initial_queries": [
    {
      "query": "家寧和 Andy 之間的糾紛內幕與最新發展：雙方聲明、事件時間線和媒體報導"
    },
    {
      "query": "眾量級頻道家寧 Andy 爭議事件始末"
    }
  ],
  "initial_responses": [
    {
      "query": "家寧和 Andy 之間的糾紛內幕與最新發展：雙方聲明、事件時間線和媒體報導",
      "results": [
        {
          "title": "家寧回擊Andy 指控私轉收益、並啟動法律程序",
          "url": "https://tw.news.yahoo.com/家寧回擊andy-指控私轉收益-並啟動法律程序-012515489.html",
          "content": "圖／家寧（右）一家人沉寂多天後，正式列出6點聲明反擊。（翻攝 眾量級 臉書）",
          "raw_content": "家寧回擊Andy 指控私轉收益、並啟動法律程序\n\n（記者廖又萱／綜合報導）曾由情侶檔組成的「眾量級」網紅頻道拆夥後...",
          "score": 0.6415577
        }
      ]
    }
  ],
  "sections": [
    {
      "title": "糾紛的起因和雙方指控",
      "description": "探討家寧和Andy糾紛的起因，以及雙方各自提出的指控和說法。",
      "search_queries": [
        {
          "query": "家寧 Andy 眾量級 糾紛 起因 指控"
        }
      ],
      "search_responses": [
        {
          "query": "家寧 Andy 眾量級 糾紛 起因 指控",
          "results": [
            {
              "title": "眾量級拆夥 家寧列6大項回應「私吞收益」指控",
              "url": "https://www.ettoday.net/news/20230714/2544579.htm",
              "content": "曾是情侶的兩人共同經營「眾量級」頻道，但近期卻爆出糾紛，Andy指控家寧切割合作關係，私自將近500萬元的收益匯入自己戶頭。",
              "raw_content": "「眾量級」的家寧與Andy近日爆發對簿公堂風波，家寧14日發6點聲明澄清，指控對方長期霸凌與言語暴力，以及假藉合作之名行控制之實。",
              "score": 0.92
            }
          ]
        }
      ]
    }
  ]
}

# 使用範例

## 安裝步驟

```bash
# 創建新的 conda 環境，指定 Python 3.11.11 版本
conda create -n web-search-agent python=3.11.11 -y

# 激活環境
conda activate web-search-agent

# 安裝相依套件
pip install -r requirements.txt

# 從 GitHub 複製專案
git clone https://github.com/your-username/web-search-agent.git
cd web-search-agent

# 配置環境變數
cp .env.example .env
# 編輯 .env 文件，填入您的 OPENAI_API_KEY 及 TAVILY_API_KEY 等必要 API 密鑰
```

## 透過 Python 代碼使用

```python
# 先去修改 ./test/test_title ISSUE_TITLE

# 測試
python ./search.py


```


## 配置選項說明

在 `config.py` 中的 `WebSearchConfig` 類提供了以下 `DEFAULT` 配置選項：

```python
WebSearchConfig(
    # LLM 配置
    llm_provider="openai",         # LLM提供者 (目前支援 "openai")
    planner_model="gpt-3.5-turbo", # 用於規劃和查詢生成的模型
    
    # 搜尋配置
    search_api="tavily",           # 搜尋API (tavily, perplexity, exa 等)
    search_api_config={},          # 搜尋API的額外配置
    
    # 查詢生成
    initial_queries_count=3,       # 初始搜尋查詢數量
    section_queries_count=2,       # 每個部分的搜尋查詢數量
    
    # 控制參數
    max_sections=5,                # 生成的最大部分數量
    include_raw_content=True,      # 是否在搜尋結果中包含原始內容
)
```

若想要修改請直接在 search.py 中修改以下程式碼

```python
config = WebSearchConfig(
    llm_provider="openai",
    planner_model="o1",
    search_api="tavily",
    search_api_config={"include_raw_content": True, "max_results": 3},
    initial_queries_count=2,
    section_queries_count=2,
    max_sections=4
)
    
```