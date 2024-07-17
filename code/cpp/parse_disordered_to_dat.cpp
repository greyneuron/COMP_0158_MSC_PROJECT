#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <pugixml.hpp>
#include <iostream>

// To compile you need to link the pugixml lib
// g++ parse_disordered_to_dat.cpp -l pugixml -o parse_disorder
// sudo parse_disorder

int main()
{
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file("extras_part_test.xml");

    // The main file is too big and will run out of memory
    //pugi::xml_parse_result result = doc.load_file("/Volumes/My Passport 3/downloads/extra.xml");

    if (result){ 
        //std::cout << "success";
    }else{
        //std::cout << "fail";
    }
    std::cout << "Load result: " << result.description();

    //simple_walker walker;
    //doc.traverse(walker);
    int record_count = 0;
    pugi::xml_node root = doc.child("root");
    pugi::xml_node protein_root = doc.child("interproextra");

    for (pugi::xml_node protein = protein_root.first_child(); protein; protein = protein.next_sibling()) {
        std::string node_name = protein.name();
        if(node_name != "protein"){
            //std::cout<< protein.name() << "not a protein" << std::endl ;
        }
        else{
            std::string protein_id = protein.attribute("id").value();
            //std::cout << "Protein id: " << protein_id << std::endl;

            // protein is now node with children whcih are matches
            for (pugi::xml_node match = protein.first_child(); match; match = match.next_sibling()) {
                std::string mobidb_match = "MOBIDBLT";
                //std::cout << match.name() << match.attribute("dbname").value() << std::endl;
                if(match.attribute("dbname").value() == mobidb_match){
                    // match is now a mobidb attribute
                    for (pugi::xml_node match_detail = match.first_child(); match_detail; match_detail = match_detail.next_sibling()) {
                        record_count +=1;
                        std::cout << record_count << "|" << protein_id << "|DISORDER|" << match_detail.attribute("sequence-feature").value() << "|" << match_detail.attribute("start").value() << "|" << match_detail.attribute("end").value() << std::endl;
                    }
                }
            }

        }
    }
}

