# 도로 밀도 시뮬레이션

## Prerequisites

> numpy  
> opencv-python  

`pip install -r requirements.txt`  


## Usage
```bash
git clone https://github.com/dh031200/toy-projects.git
cd toy-projects/road-density-simulation
python main.py
```

시뮬레이션 임의 종료는 q를 누르면 됩니다.


## CONFIG
* 에이전트 설정
    * RANDOM_EPSILON: 무작위 행동 확률(0.1)  
    * GENERATE_FREQUENCY: 인구 유입 빈도(0.8)
    * STOP_EPSILON: 가만히 서있을 확률(0.3)
    * RIGHT_SIDE_WALK: 우측보행 여부 (True)

* 시뮬레이터 설정
    * FRAME_SPEED: 배속
    * VIS_SCALE: 화면 비율 (20)
    * STUCK_LINE_LIMIT: 막힌 구간 한계치[column] (6)
    * END_COUNT: 시뮬레이션 종료 유예 (1)
    * VISUALIZE: 시각화 (True)
 
* 환경 설정
    * X: 도로길이 (80)  
    * Y: 도로 폭 (12)  
    * WALL_WIDTH: 벽 길이 (12)
    * WALL_HEIGHT: 벽 폭 (5)

* 색상
    * VIS_COLOR: Agent 색상 (0, (255, 0, 0), (0, 255, 0))
    * WALL_COLOR: 벽 색상 (150, 150, 150)
    * STUCK_COLOR: 막힌 열 색상 (0, 0, 255)
    * BORDER: 경계선 색상 (20, 20, 20)
    * TXT_COLOR: 텍스트 색상 (255, 255, 255)

***\*괄호 안의 값은 default 값 입니다.***
