# ComDon_Stock
- 🖥️컴퓨터로 돈벌자! 실시간 조건검색을 이용한 📈매매 프로젝트
- 이베스트투자증권의 조건검색에서 실시간으로 검색되는 종목을 자동으로 매수한 뒤, 원하는 익절가와 손절가에 매매를 진행합니다.
- 눌림목 매수를 원할 경우, 설정을 통해 진행할 수 있습니다.

# 실행
- pip install -r requirements.txt
- .env 파일 작성
- main.py 실행

# .env 파일 작성 내용
- `APP_KEY` = 이베스트투자증권 실제계좌의 APP_KEY입니다.
- `APP_SECRET` = 이베스트투자증권 실제계좌의 APP_SECRET입니다.

- `VIRTUAL_FLAG` = 1로 설정할 경우 모의투자 계좌로 매매, 0으로 설정할경우 실제 계좌로 매매합니다.

- `VIRTUAL_APP_KEY` = 이베스트투자증권 모의계좌의 APP_KEY입니다.
- `VIRTUAL_APP_SECRET` = 이베스트투자증권 모의계좌의 APP_SECRET입니다.

- `USER_ID` = 이베스트투자증권 ID입니다.
- `CONDITION_NAME` = 이베스트투자증권 서버에 저장한 조건검색식 이름입니다.

- `TOTAL_BALANCE` = 현재 보유 금액입니다. 설정한 금액보다 10%작은 금액을 현재 보유금액으로 생각하고 자동매매를 진행합니다.(손실 대비)
- `MAX_STOCKS` = 최대 보유 종목 수량입니다.

- `PROFIT_PERCENT_1` = 1차 익절 퍼센트입니다.
- `PROFIT_PERCENT_2` = 2차 익절 퍼센트입니다.

- `LOSS_CRITERION` = high 설정할 경우, 매수한 시점의 가격으로부터 최고가 대비 loss_percent 하락시 손절을 진행합니다. buy 일경우, 매수한 시점의 가격으로부터 loss_percent 하락시 손절을 진행합니다.
- `LOSS_PERCENT` = 손절 퍼센트입니다.

- `ADD_BUY_FLAG` = 1로 설정하면 1차 매수를 한 가격으로부터 가격이 BUY_PERCENT만큼하락했을때 추가매수를 진행합니다. (수량은 1차 매수를 했을때와 동일합니다.)
- `BUY_PERCENT` = 2차매수 퍼센트입니다. LOSS_PERCENT보다 크면 안됩니다. 0 < BUY_PERCENT < LOSS_PERCENT 2차매수의 경우도 LOSS_PERCENT에 같이 손절을 진행합니다.

- `ADD_PROFIT_PERCENT_1` = 추가매수 1차 익절 퍼센트입니다.
- `ADD_PROFIT_PERCENT_1` = 추가매수 2차 익절 퍼센트입니다.