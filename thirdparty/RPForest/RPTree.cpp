#include "RPTree.h"
#include <iostream>

void TRPTree::Build(float* Atr_min, float* Atr_max, uint32_t atr_cnt) {
  uint32_t atr_num;
 
  for(uint32_t i = 0; i < nodes_cnt; i++) {
    atr_num = (*dist_atr)(*gen_atr);
    Nodes[i].trhs = (*dist_trhs)(*gen_trhs);
    Nodes[i].trhs *= Atr_max[atr_num] - Atr_min[atr_num];
    Nodes[i].trhs += Atr_min[atr_num];
    Nodes[i].atr_num = atr_num;    
    Nodes[i].ftrhs = (float)Nodes[i].trhs;
  } 

  for(uint32_t i = 0; i <= nodes_cnt; i++) {
    Leafs[i].cnt[0] = 0;
    Leafs[i].cnt[1] = 0;
  }  
}

void TRPTree::Train(uint32_t& label, float* Atr, uint32_t& atr_cnt) {
  uint32_t cl = 0;
  uint32_t cn = 0;
  
  while(cl < h) {
    if(Atr[Nodes[cn].atr_num] > Nodes[cn].ftrhs)
      cn = cn * 2 + 2;
    else
      cn = cn * 2 + 1;
      
    cl++;
  }
  
  cn -= nodes_cnt;

  Leafs[cn].cnt[label]++;
}

void TRPTree::TrainFinalize() {
  uint32_t leaf_cnt = nodes_cnt + 1; 
  
  for(uint32_t i = 0; i < leaf_cnt; i++) {
    if(diff_priv) {
      Leafs[i].cnt[0] += (*dist_lap)(*gen_lap) * ((rand() % 2) * 2 - 1);
      Leafs[i].cnt[1] += (*dist_lap)(*gen_lap) * ((rand() % 2) * 2 - 1);
    }
    
    if(Leafs[i].cnt[0] > Leafs[i].cnt[1])
      Leafs[i].label = 0;
    else
      Leafs[i].label = 1;  
    
    //std::cout << i << "\t" << Leafs[i].cnt[0] << "\t" << Leafs[i].cnt[1] << "\t" << Leafs[i].label << "\n";
  } 
}

uint32_t TRPTree::Predict(float* Atr) {
  uint32_t cl = 0;
  uint32_t cn = 0;
  
  while(cl < h) {
    if(Atr[Nodes[cn].atr_num] > Nodes[cn].ftrhs)
      cn = cn * 2 + 2;
    else
      cn = cn * 2 + 1;
      
    cl++;
  }
  
  cn -= nodes_cnt;

  return Leafs[cn].label;
}

float TRPTree::Predict_ratio(float* Atr) {
  uint32_t cl = 0;
  uint32_t cn = 0;
  
  while(cl < h) {
    if(Atr[Nodes[cn].atr_num] > Nodes[cn].ftrhs)
      cn = cn * 2 + 2;
    else
      cn = cn * 2 + 1;
      
    cl++;
  }
  
  cn -= nodes_cnt;
  
  float cnt1 = (float)Leafs[cn].cnt[1];
  float cnt2 = (float)Leafs[cn].cnt[0];  
  if(cnt1 < 0) cnt1 = 0;    
  if(cnt2 < 0) cnt2 = 0;    
  float ratio = cnt1;
  cnt2 += cnt1;
  if(cnt2 < 1) cnt2 = 1;    
  ratio /= cnt2;
  
  return ratio;
}
