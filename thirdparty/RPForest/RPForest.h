#ifndef __RPFOREST_H__
#define __RPFOREST_H__

#include "RPTree.h"

class TRPForest {
  private:
    TRPTree** rptrees;
    uint32_t trees_cnt;
    uint8_t pred_type;
    float dist_param;
    std::default_random_engine gen_atr;
    std::default_random_engine gen_trhs;
    std::default_random_engine gen_lap;
    std::default_random_engine gen_pred;
    std::uniform_int_distribution<uint32_t>* dist_atr;
    std::uniform_real_distribution<float>* dist_trhs;
    std::exponential_distribution<float>* dist_lap;
    std::uniform_real_distribution<float>* dist_pred;
  public:  
    TRPForest() { trees_cnt = 0; };
    TRPForest(uint32_t c, uint32_t h, float v);
    void SetPredType(uint8_t pt) { pred_type = pt; };
    void SetHeight(uint32_t height);
    void Build(float* Atr_min, float* Atr_max, uint32_t atr_cnt);
    void Train(uint32_t& label, float* Atr, uint32_t& atr_cnt);
    void TrainFinalize();
    uint32_t Predict(float* Atr);
    float GetDistParam() { return dist_param; };
};

#endif
