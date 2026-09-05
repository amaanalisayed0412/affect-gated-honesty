# Source this before working: `source env.sh`
source /15tb_scratch_data/amaan/anaconda3/etc/profile.d/conda.sh
conda activate mats

export MATS_ROOT=/15tb_scratch_data/amaan/MATS
export HF_HOME=$MATS_ROOT/hf_cache
export HF_HUB_CACHE=$MATS_ROOT/hf_cache/hub
export PIP_CACHE_DIR=$MATS_ROOT/.pip-cache
export TOKENIZERS_PARALLELISM=false

# Proxy — tmux server env does NOT inherit these, so set them explicitly.
export http_proxy=http://proxy22.iitd.ac.in:3128
export https_proxy=http://proxy22.iitd.ac.in:3128
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy
export no_proxy=localhost,127.0.0.1
export NO_PROXY=$no_proxy

cd $MATS_ROOT
echo "mats env active | HF_HOME=$HF_HOME | cwd=$(pwd)"
