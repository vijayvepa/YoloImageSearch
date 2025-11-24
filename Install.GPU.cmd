
conda create --prefix ./gpu python=3.11 -y
conda activate ./gpu
conda install pytorch==2.5.1 torchvision==0.20.1 pytorch-cuda=12.4 -c pytorch -c nvidia
pip install -r requirements.txt
