#pragma once

#include <string>
#include <vector>

#include "dataframe.h"

class Path {
public:
  Path(const DataFrame& df);
  Path(const Path& other) = default;
  Path(Path&& other) = default;
  Path& operator=(const Path& other) = default;
  Path& operator=(Path&& other) = default;

  void swap(size_t i, size_t j);
  std::string to_string(std::string separator = " ") const;
  int distance_idx(int i, int j) const;
  int cost() const;
  void add(int i);
  void clear();
  size_t size() const;
  void initialize();

  int& operator[](size_t i);
  const int& operator[](size_t i) const;

private:
  std::vector<int> path_;
  const DataFrame *df_;
};

