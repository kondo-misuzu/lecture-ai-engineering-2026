# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
素のエージェントは一般論で回答していたのに対し、エージェントはAIE2026の宿題におけるレベルについて用語集を参照し、正確に回答できていた。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[tool return] search_glossary -> [{"term": "QLoRA", "lecture": 2, "definition": "ベースモデルの重みを4ビットなどに量子化してメモリを節約したうえで、LoRAで学習する手法。より大きなモデルを小さなGPUで扱える。本講座の第2…
[usage] RunUsage(cost=Decimal('0.0008063'), details={'text_prompt_tokens': 1196}, input_text_tokens=1196, input_tokens=1196, output_tokens=179, requests=2, tool_calls=2)

- 1つの質問での LLM 呼び出し回数（`requests`）：2回
- 追加したツールと、docstring に書いた説明：
--追加したツール：make_quiz
--docstringに書いた説明
"""指定した回の用語から1つを選び、確認問題と答えを返す。

  「第2回の確認問題を出して」のように、復習用の問題を求められたときに使う。
# 1. load_glossary() から lecture が一致する用語を集める
# 2. 1 つ選ぶ（random.choice ）
# 3. 問題と答えを文字列で返す（ json.dumps など）
"""

## 宿題

- 取り組んだレベル：実装にとりくんだ
- やったこと：学習の記録をlearning_log/フォルダに保存するツールsave_learning_logを実装した。具体的には、save_learning_logという、引数connetをMarkdownファイルとしてlearning_log/に保存する関数を実装し、さらにrequires_approval=Trueにすることで、ユーザの承認を待って、承認を得たら再実行するようにした。
- 結果：
「学習記録に保存して」のような入力を行うとエージェントがツールを呼び出し、学習記録に保存するための文章を生成し、保存していいかを確認するようになった。
- 気づき・疑問：
新たなツールを実装することで、エージェントができることの幅が大きく変わることがわかった。後から取り消しにくい操作の場合は、ユーザの承認を待ってから実行するべきだと理解できた。