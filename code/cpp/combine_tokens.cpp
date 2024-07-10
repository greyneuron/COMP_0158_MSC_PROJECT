#include <iostream>
#include <fstream>
#include <string>
#include <regex>

int main() {
    // Define the path to the file
    std::string protein_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat";

    
    // Open the file
    std::ifstream file(protein_file);
    
    // Check if the file was successfully opened
    if (!file.is_open()) {
        std::cerr << "Could not open the file!" << std::endl;
        return 1;
    }
    
    // Define the regular expression pattern
    std::regex pattern("([A-Z0-9]+)|");
    std::smatch matches;
    
    // Read each line from the file
    std::string line;


    while (std::getline(file, line)) {
        if(std::regex_search(line, matches, pattern)) {
            //std::cout << "Searching line: " << line << std::endl;

            std::cout << matches[0].str() << "\n";

        } else {
            std::cout << "Match not found\n";
        }
    }

   /*
    while (std::getline(file, line)) {
        // Search for the pattern in the current line
        if (std::regex_search(line, pattern)) {
            std::cout << "Match found: " << line << std::endl;
        }
    }
    */

    // Close the file
    file.close();
    
    return 0;
}
