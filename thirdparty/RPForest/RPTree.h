#ifndef __RPTREE_H__
#define __RPTREE_H__

#include <stdint.h>
#include <stdlib.h>
#include <random>

typedef struct {
  double trhs;
  float ftrhs;
  uint32_t atr_num;
} TRPTnode;

typedef struct {
  float cnt[2];
  uint32_t label;
} TRPTleaf;

class TRPTree {
  private:
    uint32_t h; //h = 0 - only root, h = 1 - 3 nodes, etc
    std::default_random_engine* gen_atr;
    std::default_random_engine* gen_trhs;    
    std::default_random_engine* gen_lap;
    std::uniform_int_distribution<uint32_t>* dist_atr;
    std::uniform_real_distribution<float>* dist_trhs;
    std::exponential_distribution<float>* dist_lap;
    uint32_t nodes_cnt;
    TRPTnode* Nodes;    
    TRPTleaf* Leafs; 
  public:  
    bool diff_priv;  
    TRPTree() { h = 0; };
    TRPTree(uint32_t height) { h = height; nodes_cnt = (1 << h) - 1; Nodes = new TRPTnode[nodes_cnt]; Leafs = new TRPTleaf[nodes_cnt + 1]; };
    void SetHeight(uint32_t height) { h = height; nodes_cnt = (1 << h) - 1; Nodes = new TRPTnode[nodes_cnt]; Leafs = new TRPTleaf[nodes_cnt + 1]; };
    void SetGenAtr(std::default_random_engine* gen) { gen_atr = gen; };
    void SetGenTrhs(std::default_random_engine* gen) { gen_trhs = gen; };
    void SetGenLap(std::default_random_engine* gen) { gen_lap = gen; };
    void SetDistAtr(std::uniform_int_distribution<uint32_t>* dist) { dist_atr = dist; };
    void SetDistTrhs(std::uniform_real_distribution<float>* dist) { dist_trhs = dist; };
    void SetDistLap(std::exponential_distribution<float>* dist) { dist_lap = dist; };
    void Build(float* Atr_min, float* Atr_max, uint32_t atr_cnt);
    void Train(uint32_t& label, float* Atr, uint32_t& atr_cnt);
    void TrainFinalize();
    uint32_t Predict(float* Atr);
    float Predict_ratio(float* Atr);
};

#endif
