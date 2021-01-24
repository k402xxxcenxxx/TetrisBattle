FROM stablebaselines/rl-baselines-zoo-cpu:v2.10.0

WORKDIR /root

RUN git clone https://github.com/k402xxxcenxxx/TetrisBattle.git

WORKDIR /root/TetrisBattle

RUN apt-get update
RUN apt-get install -y python3-tk

RUN python setup.py develop

ENTRYPOINT ["python", "train_baseline_test.py"]
