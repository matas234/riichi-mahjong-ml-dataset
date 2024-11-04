# Riichi mahjong ML dataset (Riichi, Pon, Chi, Kan)
This is the repository containing code that was used to create this riichi mahjong dataset. The dataset was aggrated from replays from Tenhou Phoenix room (top 0.1%).
The actual replays were pulled using [phoenix-logs](https://github.com/ApplySci/phoenix-logs), however I struggled to get this to work, as this did this person: (https://pathofhouou.blogspot.com/2021/04/guide-replay-analysis.html).
However, they were sent the .db files by the author of phoenix-logs and they were uploaded to this [google drive folder](https://drive.google.com/drive/u/0/folders/1danHelDPYF2YP9Er2HhJCemlVQN25nb_).
The majority of this codebase is used to parse these replays and convert them into state/label for each action (Riichi, Pon, Chi, Kan). The discard dataset can be found on [kaggle](https://www.kaggle.com/datasets/trongdt/japanese-mahjong-board-states/data), and I have adopted a very similar data structure.


