#include <string>

#include "dataframe.h"
#include "matrix.h"

using namespace std;

DataFrame::DataFrame(const string& file_name)
    : df_(read_matrix(file_name))
    , nnodes_(df_.size()) {
}

int DataFrame::distance(int i, int j) const {
  const auto& a = df_[i];
  const auto& b = df_[j];
  const auto N = a.size();
  int dist = 0;
  for (size_t k = 0; k < N; k++) {
    if (a[k] != b[k]) {
      dist += 1;
    }
  }
  return dist;
}

size_t DataFrame::size() const {
  return nnodes_;
}
