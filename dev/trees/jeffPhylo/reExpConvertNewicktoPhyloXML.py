"""
@summary: This script will convert a Nexus file from Jeff into Phylo-XML
@author: CJ Grady
@version: 1.0
@status: alpha

@license: gpl2
@copyright: Copyright (C) 2014, University of Kansas Center for Research

          Lifemapper Project, lifemapper [at] ku [dot] edu, 
          Biodiversity Institute,
          1345 Jayhawk Boulevard, Lawrence, Kansas, 66045, USA
   
          This program is free software; you can redistribute it and/or modify 
          it under the terms of the GNU General Public License as published by 
          the Free Software Foundation; either version 2 of the License, or (at 
          your option) any later version.
  
          This program is distributed in the hope that it will be useful, but 
          WITHOUT ANY WARRANTY; without even the implied warranty of 
          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
          General Public License for more details.
  
          You should have received a copy of the GNU General Public License 
          along with this program; if not, write to the Free Software 
          Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
          02110-1301, USA.
"""

#from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from LmCommon.common.elementTreeLM import Element, SubElement, tostring
import simplejson
#from LmCommon.common.lmXml import Element, SubElement, tostring

import re
from cStringIO import StringIO

nexusFn = 'bats.nex'

#nexusTree = "TREE Fig._3_and_15.1 = [&R] (outgroup_to_Chiroptera,(((((((((Eptesicus_serotinus,Eptesicus_hottentotus,Eptesicus_furinalis,Eptesicus_fuscus,Eptesicus_bottae,Eptesicus_brasiliensis,(Eptesicus_diminutus,Eptesicus_innoxius),Eptesicus_guadeloupensis,Eptesicus_tatei,Eptesicus_demissus,Eptesicus_pachyotis,Eptesicus_kobayashii,Eptesicus_platyops),(Eptesicus_nilssoni,Eptesicus_bobrinskoi),Eptesicus_nasutus),Eptesicus_floweri),((((((Pipistrellus_pipistrellus,Pipistrellus_nathusii,Pipistrellus_permixtus),((Pipistrellus_javanicus,Pipistrellus_babu,Pipistrellus_endoi,Pipistrellus_paterculus,Pipistrellus_peguensis),(Pipistrellus_mimus,Pipistrellus_tenuis,Pipistrellus_coromandra,Pipistrellus_sturdeei))),(Pipistrellus_kuhlii,Pipistrellus_aero,Pipistrellus_aegyptius,Pipistrellus_inexspectatus,Pipistrellus_maderensis,Pipistrellus_rusticus),(Pipistrellus_ceylonicus,Pipistrellus_minahassae)),(Pipistrellus_rueppelli,Pipistrellus_crassulus,Pipistrellus_nanulus)),((((Pipistrellus_ariel,Pipistrellus_bodenheimeri,Pipistrellus_savii),Pipistrellus_macrotis,Pipistrellus_cadornae),((Pipistrellus_nanus,Pipistrellus_arabicus),Pipistrellus_imbricatus),(Pipistrellus_hesperus,Pipistrellus_musciculus),(Pipistrellus_eisentrauti,Pipistrellus_anchietai),(Pipistrellus_pulveratus,(Pipistrellus_kitcheneri,Pipistrellus_lophurus))),(Pipistrellus_stenopterus,Pipistrellus_anthonyi,Pipistrellus_joffrei)),((Eptesicus_somalicus,Eptesicus_capensis,Eptesicus_brunneus,Eptesicus_guineensis,Eptesicus_melckorum),(Eptesicus_tenuipinnis,Eptesicus_flavescens,Eptesicus_rendalli)),(Pipistrellus_tasmaniensis,(Pipistrellus_affinis,Pipistrellus_mordax,Pipistrellus_petersi)),(Pipistrellus_circumdatus,Pipistrellus_cuprosus,Pipistrellus_societatis),(Eptesicus_baverstocki,Eptesicus_douglasorum,Eptesicus_pumilus,Eptesicus_regulus,Eptesicus_vulturnus,Eptesicus_sagittula)),Pipistrellus_dormeri),(Nyctalus_noctula,Nyctalus_leisleri,Nyctalus_lasiopterus,Nyctalus_aviator,Nyctalus_azoreum,Nyctalus_montanus),((Barbastella_barbastellus,Barbastella_leucomelas),(((Plecotus_rafinequii,(Plecotus_townsendii,Plecotus_mexicanus)),((Plecotus_austriacus,Plecotus_teneriffae),(Plecotus_auritus,Plecotus_taivanus))),(Idionycteris_phyllotis,Euderma_maculatum))),Pipistrellus_subflavus,Myotis,Lasionycteris_noctivagans,(((Lasiurus_borealis,Lasiurus_seminolus),Lasiurus_cinereus,Lasiurus_castaneus),(Lasiurus_ega,Lasirus_intermedius),Lasiurus_egregius),((((Rhogessa_tumida,Rhogeesa_parvula,Rhogessa_minutilla,Rhogessa_genowaysi),Rhogessa_gracilis),Rhogessa_mira),Rhogeesa_alleni),Antrozidae,Nycticeus_humeralis,Otonycteris_hemprichi,(((Scotoecus_albofuscus,Scotoecus_hirundo),Scotoecus_pallidus),((Nycticeus_balstoni,(Nycticeus_sanborni,Nycticeus_greyii)),Nycticeus_schlieffeni)),((Nyctophilus_geoffroyi,Nyctophilus_timorensis,Nyctophilus_walkeri,Nyctophilus_arnhenmensis,Nyctophilus_gouldi,Nyctophilus_microdon,Nyctophilus_microtis,Nyctophilus_heran),Pharotis_imogene),((Scotophilus_kuhlii,(Scotophilus_heathii,Scotophilus_celebensis),(Scotophilus_leucogaster,(Scotophilus_dinganii,Scotophilus_nux,Scotophilus_robustus)),Scotophilus_nigrita,(Scotophilus_viridis,Scotophilus_borbonicus)),(Scotomanes_ornatus,Scotomanes_emarginatus)),(Vespertilio_murinus,Vespertilio_superans),(Murinae,Kerivoulinae),Nycticeus_rueppellii,((Chalinolobus_gouldii,Chalinolobus_morio,Chalinolobus_nigrogriseus,Chalinolobus_picatus,Chalinolobus_dwyeri),Chalinolobus_tuberculatus),Philetor_brachypterus,(Hesperoptenus_doriae,(Hesperoptenus_blanfordi,Hesperoptenus_tickelli,Hesperoptenus_tomesi,Hesperoptenus_gaskelli)),(Histiotus_velatus,Histiotus_montanus,Histiotus_macrotis,Histiotus_alienus),Eudiscopus_denticulus,Ia_io,(Glischropus_tylopus,Glischropus_javanus),(Laephotis_wintonii,Laephotis_botswannae,Laephotis_namibensis,Laephotis_angolensis),(Tylonycteris_pachypus,Tylonycteris_robustula),Mimetillus_moloneyi,(Chalinolobus_argentatus,Chalinolobus_beatrix,Chalinolobus_poensis,Chalinolobus_variegatus,Chalinolobus_alboguttatus,Chalinolobus_egeria,Chalinolobus_gleni,Chalinolobus_kenyacola,Chalinolobus_superbus)),Miniopterinae),(Tomopeatinae,Molossidae)),(((Phyllostomidae,Mormoopidae),Noctilionidae),Mystacinidae),Myzopodidae,(Thyropteridae,(Fuuripteridae,Natalidae))),(Emballonuridae,(((Rhinopoma_muscatellum,Rhinopoma_microphyllum,Rhinopoma_hardwickii),Craseonycteridae),((Nycteridae,(Rhinolophidae,Hipposideridae)),Megadermatidae)))),Pteropodidae));"
nexusTreeMod = "Chiroptera(((((((((Eptesicus_serotinus,Eptesicus_hottentotus,Eptesicus_furinalis,Eptesicus_fuscus,Eptesicus_bottae,Eptesicus_brasiliensis,(Eptesicus_diminutus,Eptesicus_innoxius),Eptesicus_guadeloupensis,Eptesicus_tatei,Eptesicus_demissus,Eptesicus_pachyotis,Eptesicus_kobayashii,Eptesicus_platyops),(Eptesicus_nilssoni,Eptesicus_bobrinskoi),Eptesicus_nasutus),Eptesicus_floweri),((((((Pipistrellus_pipistrellus,Pipistrellus_nathusii,Pipistrellus_permixtus),((Pipistrellus_javanicus,Pipistrellus_babu,Pipistrellus_endoi,Pipistrellus_paterculus,Pipistrellus_peguensis),(Pipistrellus_mimus,Pipistrellus_tenuis,Pipistrellus_coromandra,Pipistrellus_sturdeei))),(Pipistrellus_kuhlii,Pipistrellus_aero,Pipistrellus_aegyptius,Pipistrellus_inexspectatus,Pipistrellus_maderensis,Pipistrellus_rusticus),(Pipistrellus_ceylonicus,Pipistrellus_minahassae)),(Pipistrellus_rueppelli,Pipistrellus_crassulus,Pipistrellus_nanulus)),((((Pipistrellus_ariel,Pipistrellus_bodenheimeri,Pipistrellus_savii),Pipistrellus_macrotis,Pipistrellus_cadornae),((Pipistrellus_nanus,Pipistrellus_arabicus),Pipistrellus_imbricatus),(Pipistrellus_hesperus,Pipistrellus_musciculus),(Pipistrellus_eisentrauti,Pipistrellus_anchietai),(Pipistrellus_pulveratus,(Pipistrellus_kitcheneri,Pipistrellus_lophurus))),(Pipistrellus_stenopterus,Pipistrellus_anthonyi,Pipistrellus_joffrei)),((Eptesicus_somalicus,Eptesicus_capensis,Eptesicus_brunneus,Eptesicus_guineensis,Eptesicus_melckorum),(Eptesicus_tenuipinnis,Eptesicus_flavescens,Eptesicus_rendalli)),(Pipistrellus_tasmaniensis,(Pipistrellus_affinis,Pipistrellus_mordax,Pipistrellus_petersi)),(Pipistrellus_circumdatus,Pipistrellus_cuprosus,Pipistrellus_societatis),(Eptesicus_baverstocki,Eptesicus_douglasorum,Eptesicus_pumilus,Eptesicus_regulus,Eptesicus_vulturnus,Eptesicus_sagittula)),Pipistrellus_dormeri),(Nyctalus_noctula,Nyctalus_leisleri,Nyctalus_lasiopterus,Nyctalus_aviator,Nyctalus_azoreum,Nyctalus_montanus),((Barbastella_barbastellus,Barbastella_leucomelas),(((Plecotus_rafinequii,(Plecotus_townsendii,Plecotus_mexicanus)),((Plecotus_austriacus,Plecotus_teneriffae),(Plecotus_auritus,Plecotus_taivanus))),(Idionycteris_phyllotis,Euderma_maculatum))),Pipistrellus_subflavus,Myotis,Lasionycteris_noctivagans,(((Lasiurus_borealis,Lasiurus_seminolus),Lasiurus_cinereus,Lasiurus_castaneus),(Lasiurus_ega,Lasirus_intermedius),Lasiurus_egregius),((((Rhogessa_tumida,Rhogeesa_parvula,Rhogessa_minutilla,Rhogessa_genowaysi),Rhogessa_gracilis),Rhogessa_mira),Rhogeesa_alleni),Antrozidae,Nycticeus_humeralis,Otonycteris_hemprichi,(((Scotoecus_albofuscus,Scotoecus_hirundo),Scotoecus_pallidus),((Nycticeus_balstoni,(Nycticeus_sanborni,Nycticeus_greyii)),Nycticeus_schlieffeni)),((Nyctophilus_geoffroyi,Nyctophilus_timorensis,Nyctophilus_walkeri,Nyctophilus_arnhenmensis,Nyctophilus_gouldi,Nyctophilus_microdon,Nyctophilus_microtis,Nyctophilus_heran),Pharotis_imogene),((Scotophilus_kuhlii,(Scotophilus_heathii,Scotophilus_celebensis),(Scotophilus_leucogaster,(Scotophilus_dinganii,Scotophilus_nux,Scotophilus_robustus)),Scotophilus_nigrita,(Scotophilus_viridis,Scotophilus_borbonicus)),(Scotomanes_ornatus,Scotomanes_emarginatus)),(Vespertilio_murinus,Vespertilio_superans),(Murinae,Kerivoulinae),Nycticeus_rueppellii,((Chalinolobus_gouldii,Chalinolobus_morio,Chalinolobus_nigrogriseus,Chalinolobus_picatus,Chalinolobus_dwyeri),Chalinolobus_tuberculatus),Philetor_brachypterus,(Hesperoptenus_doriae,(Hesperoptenus_blanfordi,Hesperoptenus_tickelli,Hesperoptenus_tomesi,Hesperoptenus_gaskelli)),(Histiotus_velatus,Histiotus_montanus,Histiotus_macrotis,Histiotus_alienus),Eudiscopus_denticulus,Ia_io,(Glischropus_tylopus,Glischropus_javanus),(Laephotis_wintonii,Laephotis_botswannae,Laephotis_namibensis,Laephotis_angolensis),(Tylonycteris_pachypus,Tylonycteris_robustula),Mimetillus_moloneyi,(Chalinolobus_argentatus,Chalinolobus_beatrix,Chalinolobus_poensis,Chalinolobus_variegatus,Chalinolobus_alboguttatus,Chalinolobus_egeria,Chalinolobus_gleni,Chalinolobus_kenyacola,Chalinolobus_superbus)),Miniopterinae),(Tomopeatinae,Molossidae)),(((Phyllostomidae,Mormoopidae),Noctilionidae),Mystacinidae),Myzopodidae,(Thyropteridae,(Fuuripteridae,Natalidae))),(Emballonuridae,(((Rhinopoma_muscatellum,Rhinopoma_microphyllum,Rhinopoma_hardwickii),Craseonycteridae),((Nycteridae,(Rhinolophidae,Hipposideridae)),Megadermatidae)))),Pteropodidae)"
nexusTree = "TREE Fig._3_and_15.1 = [&R] (F(A,B,(C,D)E));"# Need to process [&R] and ;
reTree = "F(A,B,(C,D)E);"
nexusTreeMod = "F(A,B,(C,D)E);"
nexusTreeMod = "(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);"


# (A,B,(C,D));                           # only leaf nodes are named
# (A,B,(C,D)E)F;                         # all nodes are named (internal nodes are E,F)
# F(A,B,(C,D));                          # no internal nodes named other than root are named e.g. E is not named 
# F(A,B,(C,D)E);                         # same as #2 but with root at beginning
# (F(A,B,(C,D)E));                       # root node enclosed by parentheses
# ((A,B,(C,D)E)F);                       # same as last one, with root enclosed but at end
# enclosed roots can also not have names for internal nodes (E)


tokens = [
    (r"\(",                         'open parens'),
    (r"\)",                         'close parens'),
    (r"[^\s\(\)\[\]\'\:\;\,]+",     'unquoted node label'),
    (r"\:[0-9]*\.?[0-9]+",          'edge length'),
    (r"\,",                         'comma'),
    (r"\[(\\.|[^\]])*\]",           'comment'),
    (r"\'(\\.|[^\'])*\'",           'quoted node label'),
    (r"\;",                         'semicolon'),
    (r"\n",                         'newline'),
]
tokenizer = re.compile('(%s)' % '|'.join([token[0] for token in tokens]))



def createClade(parent, depth, name=None):
   cladeEl = SubElement(parent, "clade", namespace=None)
   SubElement(cladeEl, "branch_length", value=depth, namespace=None)
   if name is not None:
      SubElement(cladeEl, "name", value=name, namespace=None)
   return cladeEl

def xmlify(parent, nexStr, depth=0):
   pass


def _parse_confidence(text):
   if text.isdigit():
       return int(text)
       # NB: Could make this more consistent by treating as a percentage
       # return int(text) / 100.
   try:
       return float(text)
       # NB: This should be in [0.0, 1.0], but who knows what people will do
       # assert 0 <= current_clade.confidence <= 1
   except ValueError:
       return None
        
        
def _format_comment(text):
    return '[%s]' % (text.replace('[', '\\[').replace(']', '\\]'))
    
def _get_comment(clade):
    if hasattr(clade, 'comment') and clade.comment:
        return _format_comment(str(clade.comment))
    else: return ''



class Parser(object):
   """Parse a Newick tree given a file handle.

    Based on the parser in `Bio.Nexus.Trees`.
   """
   
   def __init__(self, handle):
      self.handle = handle
      self.parentMap = {}
      self.parentDicts = {}
      
   @classmethod
   def from_string(cls, treetext):
      handle = StringIO(treetext)
      return handle
   
   def parse(self, values_are_confidence=False, comments_are_confidence=False, rooted=False):
      """Parse the text stream this object was initialized with."""
      self.values_are_confidence = values_are_confidence
      self.comments_are_confidence = comments_are_confidence
      self.rooted = rooted
      buf = ''
      for line in self.handle:
         buf += line.rstrip()
         print buf
         if buf.endswith(';'):
            phylo,phyloDict,parentDicts = self._parse_tree(buf)
            buf = ''
      if buf:
         # Last tree is missing a terminal ';' character -- that's OK
         #yield self._parse_tree(buf)
         phylo,phyloDict,parentDicts = self._parse_tree(buf)
         buf = ''
      return phylo,phyloDict,parentDicts
   
   def getParentDict(self,clade):
      return self.parentDicts[clade["pathId"]]
   
   def newCladeDict(self,parent=None,id=None):
      
      if parent is not None:
         # find the parent path
         parentPath = parent["path"]
         newClade = {}
         newClade["pathId"] = str(id)
         parent["children"].append(newClade)
         if id is not None:
            path = str(id) + ','+ parentPath
            newClade["path"] = path
         
         
         self.parentDicts[newClade["pathId"]] = parent
      else:
         newClade = {'path':'0',"pathId":"0","children":[]}
      return newClade
         
   def _parse_tree(self, text):
      """Parses the text representation into an Tree object."""
      tokens = re.finditer(tokenizer, text.strip())
      
      
      new_clade = self.new_clade
      newCladeDict = self.newCladeDict
      cladeId = 0
      root_clade = new_clade(id=cladeId)
      
      ######## JSON ###########
      rootDict = {"pathId":0,"path":'0',"children":[]} 
      #########################
      
      cladeId +=1
      
      current_clade = root_clade
      ########### JSON ###########
      currentCladeDict = rootDict
      ###########################
      entering_branch_length = False
      
      lp_count = 0
      rp_count = 0
      
      
      
      for match in tokens:
         #print "MATCH"
         token = match.group()
         
         if token.startswith("'"):
            # quoted label; add characters to clade name
            #current_clade.name = token[1:-1]
            self.add_name(current_clade, token[1:-1])
            
            ########### JSON ###################
            currentCladeDict["name"] = token[1:-1]
            ####################################
            
         elif token.startswith('['):
            # comment
            current_clade.comment = token[1:-1]
            if self.comments_are_confidence:
               # Try to use this comment as a numeric support value
               current_clade.confidence = _parse_confidence(current_clade.comment)
         
         elif token == '(':
            # start a new clade, which is a child of the current clade
            current_clade = new_clade(current_clade,id=cladeId)
            #cladeId +=1
            entering_branch_length = False
            lp_count += 1
            
            ########  JSON #####################
            currentCladeDict['children'] = []
            #currentCladeDict["pathId"] = cladeId
            tempClade = newCladeDict(currentCladeDict,id=cladeId)
            cladeId += 1
            currentCladeDict = tempClade
            
         elif token == ',':
            # if the current clade is the root, then the external parentheses are missing
            # and a new root should be created
            
            ############  JSON ###############
            if currentCladeDict["pathId"] == "0":
               rootDict = newCladeDict(id=cladeId)
               self.parentDicts[currentCladeDict["pathId"]] = rootDict
            ####################################
            if current_clade is root_clade:
               print "is it getting in here for F(A,B,(C,D)E); Answer: No"
               root_clade = new_clade(id=cladeId)
               cladeId +=1
               #current_clade.parent = root_clade
               self.parentMap[current_clade] = root_clade
               
               ############ JSON ###############
               #self.parentDicts[currentCladeDict["pathId"]] = rootDict
               #################################
            # start a new child clade at the same level as the current clade
            parent = self.process_clade(current_clade)
            current_clade = new_clade(parent,id=cladeId)
            
            ########### JSON ############
            parentDict = self.getParentDict(currentCladeDict)
            #parentDict["children"] = []
            currentCladeDict = newCladeDict(parentDict,cladeId)         
            #############################
             
            cladeId +=1
            entering_branch_length = False
            
         elif token == ')':
            # done adding children for this parent clade
            parent = self.process_clade(current_clade)
            ######### JSON #################
            parentDict = self.getParentDict(currentCladeDict)
            ###############################
            if not parent:
               print 'Parenthesis mismatch.'
            current_clade = parent
            ##########  JSON ###########
            currentCladeDict = parentDict
            
            ############################
            entering_branch_length = False
            rp_count += 1
         
         elif token == ';':
            break
         
         elif token.startswith(':'):
            # branch length or confidence
            #print "does it ever get in here, branch length"
            value = float(token[1:])
            currentCladeDict["length"] = value
            if self.values_are_confidence:
               current_clade.confidence = value
            else:
               current_clade.branch_length = value
         
         elif token == '\n':
            pass
         
         else:
            # unquoted node label
            #current_clade.name = token
            self.add_name(current_clade, token)
            
            ############ JSON ##############
            currentCladeDict["name"] = token
            ################################
      if not lp_count == rp_count:
         print 'Number of open/close parentheses do not match.'
      
      # if ; token broke out of for loop, there should be no remaining tokens
      try:
         next_token = tokens.next()
         print 'Text after semicolon in Newick tree: %s' % (next_token.group())
      except StopIteration:
         pass
      
      #self.process_clade(current_clade)
      #self.process_clade(root_clade)
      return root_clade,rootDict,self.parentDicts # Newick.Tree(root=root_clade, rooted=self.rooted)
   
   def add_name(self,clade,name):
     
      SubElement(clade, "name", name, namespace=None)
   
   def new_clade(self, parent=None, id=None):
      """Returns a new Newick.Clade, optionally with a temporary reference
      to its parent clade."""
      try:
         parentPath = parent.find("property[@ref='Lm:path']").text
         
      except:
         # doesn't have a path, means it's the root ?
         pass
      if parent is not None:
         clade = SubElement(parent, "clade", namespace=None)
         if id is not None:
            SubElement(clade, "property", value=id, namespace=None,  attribs=[('ref', 'Lm:pathId'),
                                                                             ('datatype','xsd:integer'),
                                                                             ('applies_to','clade')])
            path = str(id) + ','+ parentPath
            
            SubElement(clade, "property", value=path, namespace=None,  attribs=[('ref', 'Lm:path'),
                                                                             ('datatype','xsd:string'),
                                                                             ('applies_to','clade')])
         self.parentMap[clade] = parent
      #if path is not None:
         #SubElement(cladeEl, "path", value=path, namespace=None)
      #SubElement(cladeEl, "id", value=id, namespace=None)
      #return cladeEl
      else:
         
         clade = Element("clade",namespace=None)
         # new lines for LmXml SubElement(clade, "property", value=id, namespace=None, attrib={'ref': 'Lm:pathId',
         #                                                                'datatype': 'xsd:integer',
         #                                                                'applies_to': 'clade'})
         SubElement(clade, "property", value=id, namespace=None, attribs=[('ref', 'Lm:pathId'),
                                                                          ('datatype','xsd:integer'),
                                                                          ('applies_to','clade')])
         
         SubElement(clade, "property", value=id, namespace=None,  attribs=[('ref', 'Lm:path'),
                                                                             ('datatype','xsd:string'),
                                                                             ('applies_to','clade')])
      
      #clade = Newick.Clade()
      #clade = None
      #if parent:
      #   clade.parent = parent
      return clade
   
   def process_clade(self, clade):
      """Final processing of a parsed clade. Removes the node's parent and
      returns it."""
      #if (clade.name and not (self.values_are_confidence or self.comments_are_confidence)
      #   and clade.confidence is None):
      #   clade.confidence = _parse_confidence(clade.name)
      #   if not clade.confidence is None:
      #      clade.name = None
          
      #if hasattr(clade, 'parent'):
      #   parent = clade.parent
      #   parent.clades.append(clade)
      #   del clade.parent
      #   return parent
      return self.parentMap[clade]
      
   

def processNexusForPhyloXml(nexStr):
   if nexStr.startswith('TREE'):
      parts = nexStr.strip('TREE ').split(' = ')
      name  = parts[0]
      phylo = parts[1]
      print "name ",name
      t = Element("phyloxml", namespace=None, 
               attribs=[
                        ("xmlns", "http://www.phyloxml.org"),
                        ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"),
                        ("xmlns:Lm", "http://lifemapper.org"),  # new line
                        ("xsi:schemaLocation", "http://www.phyloxml.org http://www.phyloxml.org/1.10/phyloxml.xsd")
                       ])
      phylogenyEl = SubElement(t, "phylogeny", namespace=None, attribs=[('rooted', 'true')])
      SubElement(phylogenyEl, 'name', value=name, namespace=None)
      xmlify(phylogenyEl, phylo.strip('[&R] '))
      return t

#outStr = tostring(processNexusForPhyloXml(nexusTree))
t = open('/home/jcavner/PhyloXM_Examples/amphibiansFromNexus.nhx','r').read()
t = nexusTreeMod
sh = Parser.from_string(t) #nexusTreeMod- for bats, works
p = Parser(sh)
eTree,phyloDict,parentDicts = p.parse()

t = Element("phyloxml", namespace=None, 
              attribs=[
                       ("xmlns", "http://www.phyloxml.org"),
                       ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"),
                       ("xsi:schemaLocation", "http://www.phyloxml.org http://www.phyloxml.org/1.10/phyloxml.xsd")
                      ])
phylo = SubElement(t, "phylogeny", namespace=None, attribs=[('rooted', 'false')])
phylo.append(eTree)

outStr = tostring(t)

with open('/home/jcavner/PhyloXM_Examples/nexusTreeMod.xml', 'w') as f:
   f.write(outStr)

with open('/home/jcavner/PhyloXM_Examples/amphibianJSONDirectTest.json','w') as f:
   f.write(simplejson.dumps(phyloDict,sort_keys=True, indent=4))

   
