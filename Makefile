CC=clang++
OPT=-O3
FLAGS=-Wall
EL= # -ferror-limit=1
STD=-std=c++2a # minimum: c++17

SRC_DIR=src
MHP_SOURCES=mhp.cpp path.cpp dataframe.cpp matrix.cpp
SOURCES=$(addprefix $(SRC_DIR)/, $(MHP_SOURCES))
TARGETS=nn.out vns.out ml.out

all: $(TARGETS)

%.out: $(SRC_DIR)/%.cpp $(SOURCES)
	$(CC) $(STD) $(OPT) $(FLAGS) $(EL) $^ -o $@

clean:
	rm -f $(TARGETS)

.PHONY: all clean
