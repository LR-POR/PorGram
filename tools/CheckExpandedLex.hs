{-# LANGUAGE DeriveGeneric, OverloadedStrings #-}

module CheckExpandedLex where


import Data.Either
import System.IO
import qualified Data.Map as M
import System.Directory
import System.FilePath.Posix
import qualified Data.Text as T
import qualified Data.Text.IO as TO
import Data.List (groupBy, intercalate, sort, nub, sortOn,foldl')
import Data.List.Split (splitPlaces, chunksOf)
import Data.Maybe ( fromJust, isNothing )
import qualified Text.Regex as R
import Data.Aeson
  ( FromJSON(parseJSON)
  , Options(fieldLabelModifier)
  , ToJSON(toEncoding, toJSON)
  , defaultOptions
  , eitherDecode
  , genericParseJSON
  , genericToEncoding
  , genericToJSON
  )
import qualified Data.ByteString.Lazy as B
import qualified Data.ByteString.Lazy.Char8 as C
import GHC.Generics ( Generic )



-- apaga listas vazias
del :: [[T.Text]] -> [[T.Text]]
del (x:xs) 
 | x == [] = del xs
 | otherwise = x : del xs
del [] = []

------ construindo map das entradas do MorphoBr 

getRule :: T.Text -> M.Map T.Text [T.Text] -> T.Text
getRule tags m
 | isNothing (M.lookup tags m) = ""
 | otherwise = head $ fromJust $ M.lookup tags m

-- constrói um map do tipo lemma: [(form, regra)] ou seja, para cada lema estão associadas as 
-- entradas que possuem o mesmo
lemmaDict :: FilePath -> IO (M.Map T.Text [(T.Text, T.Text)])
lemmaDict path = do
  content <- TO.readFile path
  return $ M.fromListWith (++) $ aux (T.lines content)
 where
   aux xs = map (\s -> let p = (T.breakOn "+" (last $ T.splitOn "\t" s))
    in ((fst p), [((head (T.splitOn "\t" s)), snd p)])) xs

-- constrói um map do tipo tags: [regra] para relacionar as tags do MorphoBr às regras 
-- do arquivo my-irules.tdl
tag2rule :: FilePath -> IO (M.Map T.Text [T.Text])
tag2rule path = do
  content <- TO.readFile path
  return $ M.fromListWith (++) $ map aux (T.lines content)
 where
   aux = \s -> let p = T.splitOn "|" s in (head p, [last p])


getLex :: M.Map T.Text [T.Text]  -> FilePath -> IO [(T.Text,(T.Text,T.Text))]
getLex mtags path = do
    content <- TO.readFile path
    return $ aux mtags (T.lines content)
 where
    aux m xs = map (\s -> let p = (T.splitOn ")" (last $ T.splitOn "(" s))
     in ((T.strip $ T.toLower $ head (T.splitOn "(" s)),((T.strip $ T.toLower (last p)),getRule (head p) m))) xs


getLex2 :: M.Map T.Text [T.Text]  -> FilePath -> IO (M.Map T.Text [(T.Text, T.Text)])
getLex2 mtags path = do
    content <- TO.readFile path
    return $ M.fromListWith (++) $ nub $ aux mtags (T.lines content)
 where
    aux m xs = map (\s -> let p = (T.splitOn ")" (last $ T.splitOn "(" s))
     in ((T.strip $ T.toLower $ head (T.splitOn "(" s)),[((T.strip $ T.toLower (last p)),getRule (head p) m)])) xs

------ comparando formas
-- verifica se a forma é esta no MorphoBr, se não estiver retorna a forma e a regra 
isRegular :: (T.Text,T.Text) -> T.Text ->  M.Map T.Text [(T.Text,T.Text)] -> [T.Text]
isRegular forma lema morpho
 | elem forma (fromJust $ M.lookup lema morpho) = []
 | otherwise = [lema, fst forma, snd forma]


testEmpty :: T.Text -> M.Map T.Text [(T.Text,T.Text)] -> [(T.Text,T.Text)]
testEmpty lema morpho 
 | isNothing (M.lookup lema morpho) = []
 | otherwise = (fromJust $ M.lookup lema morpho)

-- para cada lema do map, a função verifica se suas formas são regulares, chamando a função isRegular
-- e concatenando a saída
getIrregs :: [(T.Text,(T.Text,T.Text))] -> M.Map T.Text [(T.Text,T.Text)] -> [[T.Text]]
getIrregs xs m = map (aux m) xs
 where
   aux morpho (lema,forma)
    | (snd forma) == "" = []
    | null (testEmpty lema morpho) = []
    | otherwise = isRegular forma lema morpho

getIrregs2 :: [(T.Text,[(T.Text,T.Text)])] -> M.Map T.Text [(T.Text,T.Text)] -> [[T.Text]]
getIrregs2 xs m = concatMap ((\m (lema,ys) -> map (aux m lema) ys) m) xs
 where
   aux morpho lema forma
    | null (testEmpty lema morpho) = []
    | otherwise = isRegular forma lema morpho

-- recebe dois paths, um com o diretório dos arquivos a serem verificados e outro onde serão 
-- escritas as formas irregulares
mkIrregsTab :: FilePath -> FilePath -> FilePath -> IO ()
mkIrregsTab dir lex outpath = do
  mtags <- tag2rule "etc/expanded_lex_tags.dict"
  paths <- listDirectory dir
  lex <- getLex mtags lex
  dicts <- mapM (lemmaDict . combine dir) paths
  TO.writeFile outpath (aux $ getIrregs (nub lex) (foldr (M.unionWith (++)) M.empty dicts))
 where
   aux x = T.intercalate "\n" $ map (T.intercalate "\t") $ del x

check :: FilePath -> FilePath -> FilePath -> IO ()
check dir lex outpath = do
  mtags <- tag2rule "etc/expanded_lex_tags.dict"
  paths <- listDirectory dir
  lex <- getLex2 mtags lex
  dicts <- mapM (lemmaDict . combine dir) paths
  TO.writeFile outpath (aux $ getIrregs2 (M.toList $ foldr (M.unionWith (++)) M.empty dicts) lex)
 where
   aux x = T.intercalate "\n" $ map (T.intercalate "\t") $ del x
