#pragma once

#include <string>

#include "matrix.h"

class DataFrame {
public:
  DataFrame(const std::string& file_name);
  int distance(int i, int j) const;
  size_t size() const;

private:
  const matrix_t df_;
  const size_t nnodes_;
};

