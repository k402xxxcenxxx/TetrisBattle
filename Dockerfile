FROM stablebaselines/stable-baselines

COPY ./ /root/TetrisBattle 

WORKDIR /root/TetrisBattle

RUN apt-get update
RUN apt-get install -y python3-tk

RUN python setup.py develop

ENTRYPOINT ["python", "train_baseline_test.py"]
