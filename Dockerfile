FROM stablebaselines/rl-baselines-zoo-cpu:v2.10.0

WORKDIR /root

RUN git clone https://github.com/k402xxxcenxxx/TetrisBattle.git

WORKDIR /root/TetrisBattle

RUN python setup.py develop

ENTRYPOINT ["python", "train_dqn.py"]
