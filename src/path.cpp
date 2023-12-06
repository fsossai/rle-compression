#include <sstream>
#include <string>

#include "path.h"

using namespace std;

Path::Path(const DataFrame& df) 
    : df_(&df) {
  path_.reserve(df.size());
}

int Path::cost() const {
  const auto N = path_.size();
  int c = 0;

  for (size_t i = 0; i < N-1; i++) {
    c += df_->distance(path_[i], path_[i+1]);
  }
  return c;
}

void Path::swap(size_t i, size_t j) {
  auto tmp = path_[i];
  path_[i] = path_[j];
  path_[j] = tmp;
}

string Path::to_string(string separator) const {
  stringstream ss;

  for (size_t i = 0; i < size()-1; i++) {
    ss << path_[i] << separator;
  }
  ss << path_[path_.size()-1];
  string result = ss.str();

  return result;
}

int Path::distance_idx(int i, int j) const {
  return df_->distance(path_[i], path_[j]);
}

void Path::add(int i) {
  path_.push_back(i);
}
void Path::clear() {
  path_.clear();
}

size_t Path::size() const {
 return path_.size();
}

void Path::initialize() {
  path_.clear();
  path_.reserve(df_->size());
  const auto N = df_->size();

  for (int i = 0; i < N; i++) {
    path_.push_back(i);
  }
}

int& Path::operator[](size_t i) {
  return path_[i];
}

const int& Path::operator[](size_t i) const {
  return path_[i];
}

