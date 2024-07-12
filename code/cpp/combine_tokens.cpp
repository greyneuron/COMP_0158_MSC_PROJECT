#include <iostream>
#include <fstream>
#include <string>
#include <regex>

int main() {
    // Define the path to the file
    std::string protein_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/proteins_ordered.dat";
    std::string pfam_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat";
    
    // Open the file
    std::ifstream file(protein_file);
    std::ifstream f2(pfam_file);
    
    // Check if the file was successfully opened
    if (!file.is_open()) {
        std::cerr << "Could not open the file!" << std::endl;
        return 1;
    }
    
    // Define the regular expression pattern
    std::regex pattern("([A-Z0-9]+)|");
    std::smatch matches;
    std::smatch matches_2;
    
    // Read each line from the file
    std::string line;
    std::string line_2;
    std::string protein_id;

    while (std::getline(file, line)) {
        if(std::regex_search(line, matches, pattern)) {
            //std::cout << "Searching line: " << line << std::endl;

            protein_id = matches[0];
            //std::cout << matches[0].str() << "\n";
            std::cout << protein_id << "\n";
            
            std::string pattern_2_term = "^" + protein_id + ".PF";
            std::regex pattern_2(pattern_2_term);

            //std::cout << "pattern :" + pattern_2_term << "\n";

            int counter = 0;
            while (std::getline(f2, line_2)) {
                //std::cout << "Processing line " << counter << "\n";
                //std::cout << "Searching pfam line " <<  line_2 << " for protein:" << protein_id << " with pattern " << pattern_2_term <<"\n";
                if(std::regex_search(line_2, matches_2, pattern_2)) {
                    std::cout << "Match found for " << protein_id << " : " << line_2 <<"\n";
                }
                counter +=1;
            }
            std::cout << "Finshed search for " << protein_id << "\n";
            
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
