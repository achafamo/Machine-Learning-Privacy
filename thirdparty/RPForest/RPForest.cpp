#include "RPForest.h"
#include <iostream>
TRPForest::TRPForest(uint32_t c, uint32_t h, float v) {
  uint32_t i;
  
  trees_cnt = c;
  dist_param = v;
  if(dist_param > 0)
    dist_param /= c;
  rptrees = new TRPTree* [c];
  
  gen_atr.seed(1);
  gen_trhs.seed(2);
  gen_lap.seed(3);
  gen_pred.seed(4);
  
  for(i = 0; i < c; i++) {
    rptrees[i] = new TRPTree(h);
    rptrees[i]->SetGenAtr(&gen_atr);
    rptrees[i]->SetGenTrhs(&gen_trhs);
    rptrees[i]->SetGenLap(&gen_lap);
  }
}

void TRPForest::SetHeight(uint32_t height) {
  uint32_t i;
  
  for(i = 0; i < trees_cnt; i++)
    rptrees[i]->SetHeight(height);
}

void TRPForest::Build(float* Atr_min, float* Atr_max, uint32_t atr_cnt){
  uint32_t i;
  bool diff_priv = false;
  
  if(dist_atr == NULL)
  {    
    dist_atr = new std::uniform_int_distribution<uint32_t>(0, atr_cnt - 1);
    dist_trhs = new std::uniform_real_distribution<float>(0, 1);    
  }
  
  dist_pred = new std::uniform_real_distribution<float>(0, 1);
  dist_lap = new std::exponential_distribution<float>(dist_param); 
    
  if(dist_param > 0)
    diff_priv = true;
    
  for(i = 0; i < trees_cnt; i++) {
    rptrees[i]->SetDistAtr(dist_atr);
    rptrees[i]->SetDistTrhs(dist_trhs);
    rptrees[i]->SetDistLap(dist_lap);
    rptrees[i]->Build(Atr_min, Atr_max, atr_cnt);
    rptrees[i]->diff_priv = diff_priv;
  }
}

void TRPForest::Train(uint32_t& label, float* Atr, uint32_t& atr_cnt){
  uint32_t i;
  
  for(i = 0; i < trees_cnt; i++)
    rptrees[i]->Train(label, Atr, atr_cnt);
}

void TRPForest::TrainFinalize(){
  uint32_t i;
  
  for(i = 0; i < trees_cnt; i++)
    rptrees[i]->TrainFinalize();
}

uint32_t TRPForest::Predict(float* Atr){
  uint32_t i;
  uint32_t labels_cnt[2] = {0, 0};
  float ratio = 0;
  
  switch(pred_type) {
    case 1:
      for(i = 0; i < trees_cnt; i++) {
        ratio += rptrees[i]->Predict_ratio(Atr);
      }
      ratio /= trees_cnt;
      
      if(ratio < 0.5)
        return 0;
      else
        return 1;
      break;
      
    case 2:
      for(i = 0; i < trees_cnt; i++) {
        ratio += rptrees[i]->Predict_ratio(Atr);
      }
      ratio /= trees_cnt;
      
      if(ratio < (*dist_pred)(gen_pred))
        return 0;
      else
        return 1;   
      break;
      
    default:
      for(i = 0; i < trees_cnt; i++) {
        labels_cnt[rptrees[i]->Predict(Atr)]++;
      }
      
      if(labels_cnt[0] > labels_cnt[1])
        return 0;
      else
        return 1;
  }  
}
