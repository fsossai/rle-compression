#include <iostream>
#include <sstream>
#include <fstream>
#include <chrono>

#include "matrix.h"

using namespace std;
using namespace std::chrono;

matrix_t read_matrix(const string& input_filename, const char separator) {
  cout << "Reading file ... " << flush;
  auto timer_start = high_resolution_clock::now();
  ifstream infile(input_filename);

  if (!infile.is_open()) {
    cerr << "ERROR: cannot opening file: " << input_filename << endl;
    return {};
  }

  matrix_t matrix;
  string line;

  while (getline(infile, line)) {
    vector<int> row;
    istringstream iss(line);
    
    int value;
    while (iss >> value) {
      row.push_back(value);
      if (iss.peek() == separator)
        iss.ignore();
    }
    matrix.push_back(row);
  }
  infile.close();

  int elapsed = duration_cast<milliseconds>(
      high_resolution_clock::now() - timer_start).count();
  printf("done in %.1f s\n", elapsed/1000.f);

  return matrix;
}

void print_matrix(const matrix_t& matrix) {
  for (const auto& row : matrix) {
    for (int value : row) {
      cout << value << " ";
    }
    cout << "\n";
  }
}

