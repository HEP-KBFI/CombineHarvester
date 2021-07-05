#!/bin/bash

era=$1

if [[ "$era" != "2016" ]] && [[ "$era" != "2017" ]] && [[ "$era" != "2018" ]]; then
  echo "Invalid era: $era";
  exit 1;
fi

shift
channels_all="0l_2tau 1l_1tau 1l_2tau 2l_2tau 2lss_1tau 2los_1tau 3l_1tau"
channels_args="$@"
if [ -z "$channels_args" ]; then
  channels=$channels_all;
else
  for channel_arg in $channels_args; do
    found_channel=false;
    for channel in $channels_all; do
      if [ "$channel_arg" = "$channel" ]; then
        found_channel=true;
        break;
      fi
    done
    if [ $found_channel = false ]; then
      echo "Invalid channel: $channel_arg";
      exit 1;
    fi
  done
  channels=$channels_args;
fi

declare -A outputvar_map
outputvar_map["0l_2tau"]="mvaOutput_Legacy"
outputvar_map["1l_1tau"]="mvaOutput_Legacy_6"
outputvar_map["1l_2tau"]="mvaOutput_legacy"
outputvar_map["2l_2tau"]="mvaOutput_final"
outputvar_map["2lss_1tau"]="mvaOutput_final"
outputvar_map["2los_1tau"]="mvaOutput_legacy"
outputvar_map["3l_1tau"]="mvaOutput_legacy"

declare -A stxs_map
stxs_map["0l_2tau"]="stxs_0l_2tau_0l_2tau_mvaOutput_Legacy_OS"
stxs_map["1l_1tau"]="stxs_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled"
stxs_map["1l_2tau"]="stxs_1l_2tau_mvaOutput_legacy_OS"
stxs_map["2l_2tau"]="stxs_2l_2tau_lepdisabled_taudisabled_sumOS_mvaOutput_final"
stxs_map["2lss_1tau_rest"]="stxs_2lss_1tau_sumOS_output_NN_rest"
stxs_map["2lss_1tau_ttH"]="stxs_2lss_1tau_sumOS_output_NN_ttH"
stxs_map["2lss_1tau_tH"]="stxs_2lss_1tau_sumOS_output_NN_tH"
stxs_map["2los_1tau"]="stxs_2los_1tau_mvaOutput_legacy"
stxs_map["3l_1tau"]="stxs_3l_1tau_OS_mvaOutput_legacy"

basetopdir=$PWD/cards
if [ ! -d $basetopdir ]; then
  mkdir -p $basetopdir
  tar -C $basetopdir -I lz4 -xvf /hdfs/local/karl/archives/HIG-19-008/ttHAnalysis_stxs_2020Jun18.tar.lz4
fi

topdir=$basetopdir/$era
mkdir -p $topdir

fullypatched_dir=$basetopdir/fullyPatched
minimallypatched_dir=$basetopdir/minimallyPatched

mkdir -p $fullypatched_dir
if [ "$RUN_MINIMAL" = 1 ]; then
  mkdir -p $minimallypatched_dir
fi

for channel in $channels; do
  resultsdir=$topdir/2020Jun18/datacards/$channel/results
  mkdir -p $resultsdir

  logdir=$topdir/2020Jun18/logs/$channel
  mkdir -p $logdir

  subchannels=$channel
  if [ $channel = "2lss_1tau" ]; then
    subchannels="${channel}_rest ${channel}_tH ${channel}_ttH"
  fi
  echo "Subchannels are: $subchannels";

  for subchannel in $subchannels; do
    input_orig=$topdir/2020Jun18/datacards/$channel/stxs/${stxs_map[$subchannel]}.root

    if [ ! -f $input_orig ]; then
      echo "No such file: $input_orig"
      exit 1
    fi

    merge_htxs_output_base=$resultsdir/${stxs_map[$subchannel]}
    merge_htxs_output_mod_root=${merge_htxs_output_base}_mod.root
    merge_htxs_output_mod_txt=${merge_htxs_output_base}_mod.txt

    set -x
    /usr/bin/time --verbose WriteDatacards.py --era $era --shapeSyst \
      --inputShapes $input_orig --channel $subchannel --cardFolder $resultsdir \
      --noX_prefix --forceModifyShapes &> $logdir/out_$subchannel.log
    set +x

    final_results_base=$fullypatched_dir/ttH_${subchannel}_${era}
    final_results_root=${final_results_base}.root
    final_results_txt=${final_results_base}.txt

    sort_histograms.py $merge_htxs_output_mod_root $final_results_root
    mv -v $merge_htxs_output_mod_txt  $final_results_txt

    rename_dcards.py $final_results_txt

    if [ "$RUN_MINIMAL" = 1 ]; then
      # rerunning with --minimal-patch
      # also consider: --disable-FRxt
      set -x
      /usr/bin/time --verbose WriteDatacards.py --era $era --shapeSyst --minimal-patch \
        --inputShapes $input_orig --channel $subchannel --cardFolder $resultsdir \
        --noX_prefix --forceModifyShapes &> $logdir/out_${subchannel}_minimal.log
      set +x

      final_results_base_minimal=$minimallypatched_dir/ttH_${subchannel}_${era}
      final_results_minimal_root=${final_results_base_minimal}.root
      final_results_minimal_txt=${final_results_base_minimal}.txt

      sort_histograms.py $merge_htxs_output_mod_root $final_results_minimal_root
      mv -v $merge_htxs_output_mod_txt  $final_results_minimal_txt

      rename_dcards.py $final_results_minimal_txt
    fi

  done
done
