#include <fstream>
#include <iostream>

#include "mhp.h"

using namespace std;

int main(int argc, char *argv[]) {
  if (argc < 3) {
    cout << "Usage: " << argv[0] << " INPUT LISTS OUTPUT\n";
    return 1;
  }

  const string input_filename = argv[1];
  const string lists_filename = argv[2];
  const string output_filename = argv[3];

  auto dataframe = DataFrame(input_filename);
  auto lists = read_matrix(lists_filename);
  auto path = multi_list(dataframe, lists);
  auto output_file = ofstream(output_filename);

  output_file << path.to_string("\n") << endl;
  printf("Path exported\n");

  return 0;
}
