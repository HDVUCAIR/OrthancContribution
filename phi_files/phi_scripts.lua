-- ======================================================
function trim(s)
    return (s:gsub("^%s*(.-)%s*$", "%1"))
end

-- -- ======================================================
-- function SplitToKeyList(aInputStr, aSep)
--    if aSep == nil then
--       aSep = "%s"
--    end
--    local t={}
--    for str in string.gmatch(aInputStr, "([^"..aSep.."]+)") do
--       t[str] = true
--    end
--    return t
-- end
-- 
-- -- ======================================================
-- function OpenSQL()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     local lOrthancConfig = GetOrthancConfiguration()
--     local lUser, lPass, lHost, lPort
--     if lOrthancConfig['PostgreSQL'] then
--         lUser = lOrthancConfig['PostgreSQL']['Username']
--         lPass = lOrthancConfig['PostgreSQL']['Password']
--         lHost = lOrthancConfig['PostgreSQL']['Host']
--         lPort = math.floor(lOrthancConfig['PostgreSQL']['Port']+0.5)
--     else
--         lUser = os.getenv('ORTHANC__POSTGRESQL__USERNAME')
--         lPass = os.getenv('ORTHANC__POSTGRESQL__PASSWORD')
--         lHost = os.getenv('ORTHANC__POSTGRESQL__HOST')        
--         lPort = 5432
--     end
--     local lSQLStatus
--     if not gSQLOpen then
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Loading postgres engine') end
--         gSQLEngine = require "luasql.postgres"
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Calling postgres engine') end
--         lSQLStatus, gSQLEnviron = pcall(gSQLEngine.postgres)
--         if not lSQLStatus then error("Problem starting SQL engine") end
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Connecting to database') end
--         lSQLStatus, gSQLConn = pcall(gSQLEnviron.connect,gSQLEnviron,
--                                  'philookup', lUser, lPass, lHost,lPort)
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Connection status', lSQLStatus) end
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Database', gSQLConn) end
--         if not lSQLStatus then error("Problem connecting to remote postgres") end
--         gSQLOpen = true
--     end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- -- ======================================================
-- function CloseSQL()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     if gSQLOpen then
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'Setting autocommit to true') end
--         gSQLConn:setautocommit(true)
--         if not pcall(gSQLConn.close,gSQLConn) then 
--             error("Problem closing sql connection") 
--         end
--         if not pcall(gSQLEnviron.close,gSQLEnviron) then
--             error("Problem closing sql environment")
--         end
--         gSQLConn = nil
--         gSQLEnviron = nil
--         gSQLOpen = false
--     end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end 
-- 
-- -- ======================================================
-- function CreateLookupTablesSQL()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     gIndent = gIndent + 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--     local lSQLResult = gSQLConn:setautocommit(false)
--     local lSQLStatus
--     local lSQLQuery = [[CREATE TABLE patientid 
--                        (
--                            pid SERIAL PRIMARY KEY, 
--                            value text UNIQUE NOT NULL, 
--                            parent_pid INTEGER DEFAULT NULL, 
--                            FOREIGN KEY (parent_pid) REFERENCES patientid(pid)
--                        )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating patientid table")
--     end
--     lSQLQuery = [[CREATE TABLE patientid_anon 
--                  (
--                      pid_a SERIAL PRIMARY KEY, 
--                      value text UNIQUE NOT NULL, 
--                      pid integer REFERENCES patientid
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating patientid_anon table")
--     end
--     lSQLQuery = [[CREATE TABLE studyinstanceuid 
--                  (
--                      siuid SERIAL PRIMARY KEY, 
--                      value text UNIQUE NOT NULL, 
--                      pid integer REFERENCES patientid
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating studyinstanceuid table")
--     end
--     lSQLQuery = [[CREATE TABLE studyinstanceuid_anon 
--                  (
--                      siuid_a SERIAL PRIMARY KEY, 
--                      value text UNIQUE NOT NULL, 
--                      siuid integer REFERENCES studyinstanceuid (siuid)
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating studyinstanceuid_anon table")
--     end
--     lSQLQuery = [[CREATE TABLE siuid2patientname_anon 
--                  (
--                      pna_id SERIAL PRIMARY KEY, 
--                      patientname_anon text, 
--                      timestamp TIMESTAMP,
--                      siuid integer REFERENCES studyinstanceuid (siuid)
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating siuid2patientname_anon table")
--     end
--     lSQLQuery = [[CREATE TABLE shiftepoch 
--                  (
--                      se SERIAL PRIMARY KEY, 
--                      value integer DEFAULT 0, 
--                      pid integer REFERENCES patientid
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating shiftepoch table")
--     end
--     lSQLQuery = [[CREATE TABLE internalnumber 
--                  (
--                      inid SERIAL PRIMARY KEY, 
--                      value integer UNIQUE NOT NULL, 
--                      pid integer REFERENCES patientid
--                  )]]
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem creating internalnumber table")
--     end
--     lSQLResult = gSQLConn:commit()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--     lSQLResult = gSQLConn:setautocommit(true)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
--     return true
-- 
-- end

-- -- ======================================================
-- function ConfirmLookupTablesSQL()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     local lSQLQuery = [[SELECT table_name 
--                        FROM information_schema.tables 
--                        WHERE table_name='patientid']]
--     local lSQLStatus, lSQLCursor
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Problem searching for patientid table")
--     end
--     if lSQLCursor:numrows() == 0 then
--         local lSQLResult = CreateLookupTablesSQL() 
--         if not lSQLResult then
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--             if gIndent > 0 then gIndent = gIndent - 3 end
--             return false
--         end
--     end
-- 
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end

-- -- ======================================================
-- function SetScreenOrDiagnostic(aoStudyID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagScreening = false
--     local lPatientIDModifier = 'd'
--     local loStudyInstancesMeta = 
--         ParseJson(RestApiGet('/studies/' .. aoStudyID .. '/instances', 
--                              false))
--     local lDicomFields = { 'Study', 'Series', 'PerformedProcedureStep', 
--                            'RequestedProcedure' }
--     for i, loInstanceTable in pairs(loStudyInstancesMeta) do
--         local loInstanceID = (loInstanceTable['ID'])
--         local loInstanceMeta = 
--                 ParseJson(RestApiGet('/instances/' .. 
--                                      loInstanceID .. '/simplified-tags', false))
--         for j, lDicomField in pairs(lDicomFields) do
--             local lDescriptionField = lDicomField .. 'Description'
--             if loInstanceMeta[lDescriptionField] then
--                 local lDescriptionLower = string.lower(loInstanceMeta[lDescriptionField])
--                 lFlagScreening = lFlagScreening or string.find(lDescriptionLower, 'screen')
--                 lFlagScreening = lFlagScreening or string.find(lDescriptionLower, 'scrn')
--                 if lFlagScreening then 
--                     lPatientIDModifier = 's'
--                     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--                     gIndent = gIndent - 3
--                     if gIndent > 0 then gIndent = gIndent - 3 end
--                     return lPatientIDModifier
--                 end
--             end
--         end
--         if (not lFlagScreening) and loInstanceMeta['ProcedureCodeSequence'] then
--             if loInstanceMeta['ProcedureCodeSequence'][1] then
--                 if loInstanceMeta['ProcedureCodeSequence'][1]['CodeMeaning'] then
--                     lDescriptionLower = string.lower(loInstanceMeta['ProcedureCodeSequence'][1]['CodeMeaning'])
--                     lFlagScreening = lFlagScreening or string.find(lDescriptionLower, 'screen')
--                     lFlagScreening = lFlagScreening or string.find(lDescriptionLower, 'scrn')
--                 end
--             end
--         end
--         if lFlagScreening then 
--             lPatientIDModifier = 's'
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--             gIndent = gIndent - 3
--             if gIndent > 0 then gIndent = gIndent - 3 end
--             return lPatientIDModifier
--         end
--     end
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPatientIDModifier
-- 
-- end

-- -- ======================================================
-- function Set2DOrCViewTomo(aoSeriesMeta)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagNon2D = false
--     local lPatientIDModifier = '2d'
--     for i, loInstanceID in pairs(aoSeriesMeta['Instances']) do
--         local loInstanceMeta = 
--                 ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/simplified-tags', false))
--         if loInstanceMeta['SeriesDescription'] then
--             local lDescriptionLower = string.lower(loInstanceMeta['SeriesDescription'])
--             lFlagNon2D = lFlagNon2D or string.find(lDescriptionLower, 'c-view')
--             lFlagNon2D = lFlagNon2D or string.find(lDescriptionLower, 'tomo')
--         end
--         if lFlagNon2D then 
--             lPatientIDModifier = 'n2d'
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--             gIndent = gIndent - 3
--             if gIndent > 0 then gIndent = gIndent - 3 end
--             return lPatientIDModifier
--         end
--     end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     gIndent = gIndent - 3
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPatientIDModifier
-- 
-- end
-- 
-- -- ======================================================
-- function GetPatientIDs(aoStudyMeta,aPatientIDModifier)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local ldPatientID
--     local ldPatientIDMain = {}
--     local ldPatientIDAlt = {}
--     -- Old style where other patient ids were stored at the study level
--     if aoStudyMeta['PatientMainDicomTags']['PatientID'] then
--         if string.len(trim(aoStudyMeta['PatientMainDicomTags']['PatientID'])) > 0 then
--             ldPatientID = aoStudyMeta['PatientMainDicomTags']['PatientID'] .. aPatientIDModifier
--             ldPatientIDMain[ldPatientID] = true
--         end
--     end
--     if aoStudyMeta['PatientMainDicomTags']['OtherPatientIDs'] then
--         if string.len(trim(aoStudyMeta['PatientMainDicomTags']['OtherPatientIDs'])) > 0 then
--             ldPatientID = aoStudyMeta['PatientMainDicomTags']['OtherPatientIDs'] .. aPatientIDModifier
--             ldPatientIDAlt[ldPatientID] = true
--         end
--     end
--     if aoStudyMeta['PatientMainDicomTags']['RETIRED_OtherPatientIDs'] then
--         if string.len(trim(aoStudyMeta['PatientMainDicomTags']['RETIRED_OtherPatientIDs'])) > 0 then
--             ldPatientID = aoStudyMeta['PatientMainDicomTags']['RETIRED_OtherPatientIDs'] .. aPatientIDModifier
--             ldPatientIDAlt[ldPatientID] = true
--         end
--     end
--     if aoStudyMeta['PatientMainDicomTags']['OtherPatientIDsSequence'] then
--         for i, otherPatientID in ipairs(aoStudyMeta['PatientMainDicomTags']['OtherPatientIDsSequence']) do
--             if otherPatientID['PatientID'] then
--                 if string.len(trim(otherPatientID['PatientID'])) > 0 then
--                     ldPatientID = otherPatientID['PatientID'] .. aPatientIDModifier
--                     ldPatientIDAlt[ldPatientID] = true
--                 end
--             end
--         end
--     end
--     -- Now we have to dig into at least one instance to get at the other patient ids
--     local loInstances = ParseJson(RestApiGet('/studies/' .. aoStudyMeta['ID'] .. '/instances', false))
--     local loInstanceID = loInstances[1]['ID']
--     local loInstanceMeta = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/tags?simplify', false))
--     if loInstanceMeta['PatientID'] then
--         if string.len(trim(loInstanceMeta['PatientID'])) > 0 then
--             ldPatientID = loInstanceMeta['PatientID'] .. aPatientIDModifier
--             ldPatientIDMain[ldPatientID] = true
--         end
--     end
--     if loInstanceMeta['OtherPatientIDs'] then
--         if string.len(trim(loInstanceMeta['OtherPatientIDs'])) > 0 then
--             ldPatientID = loInstanceMeta['OtherPatientIDs'] .. aPatientIDModifier
--             ldPatientIDAlt[ldPatientID] = true
--         end
--     end
--     if loInstanceMeta['RETIRED_OtherPatientIDs'] then
--         if string.len(trim(loInstanceMeta['RETIRED_OtherPatientIDs'])) > 0 then
--             ldPatientID = loInstanceMeta['RETIRED_OtherPatientIDs'] .. aPatientIDModifier
--             ldPatientIDAlt[ldPatientID] = true
--         end
--     end
--     if loInstanceMeta['OtherPatientIDsSequence'] then
--         for i, otherPatientID in ipairs(loInstanceMeta['OtherPatientIDsSequence']) do
--             if otherPatientID['PatientID'] then
--                 if string.len(trim(otherPatientID['PatientID'])) > 0 then
--                     ldPatientID = otherPatientID['PatientID'] .. aPatientIDModifier
--                     ldPatientIDAlt[ldPatientID] = true
--                 end
--             end
--         end
--     end
-- 
--     local lPatientIDs = {}
--     local lPatientIDsCount = 0
--     local ldPatientIDs = {}
--     for ldPatientID, dumby in pairs(ldPatientIDMain) do
--         if not ldPatientIDs[ldPatientID] then
--             lPatientIDsCount = lPatientIDsCount + 1
--             lPatientIDs[lPatientIDsCount] = ldPatientID
--             ldPatientIDs[ldPatientID] = true
--         end
--     end
--     for ldPatientID, dumby in pairs(ldPatientIDAlt) do
--         if not ldPatientIDs[ldPatientID] then
--             lPatientIDsCount = lPatientIDsCount + 1
--             lPatientIDs[lPatientIDsCount] = ldPatientID
--             ldPatientIDs[ldPatientID] = true
--         end
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPatientIDs
-- 
-- end
-- 
-- -- ======================================================
-- function TestGetPatientIDs(aoOrthancStudyID)
-- 
--     loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoOrthancStudyID, false))
--     aPatientIDModifier = 'zzz'
--     local lPatientIDs_lua = {}
--     lPatientIDs_lua = GetPatientIDs(loStudyMeta,aPatientIDModifier) 
--     local lPostData = {}
--     lPostData['OrthancStudyID'] = aoOrthancStudyID
--     if aPatientIDModifier then lPostData['PatientIDModifier'] = aPatientIDModifier end
--     local lPatientIDs_python = {}
--     local lResult = ParseJson(RestApiPost('/get_patient_ids_lua', DumpJson(lPostData), false))
--     for i, lIndex in ipairs(lResult['indices']) do
--         lPatientIDs_python[lIndex] = lResult['patient_ids'][i]
--     end
--     print(lPatientIDs_lua)
--     print(lPatientIDs_python)
--     PrintRecursive(lPatientIDs_lua)
--     PrintRecursive(lPatientIDs_python)
-- 
-- end
-- 
-- -- ======================================================
-- function TestSavePatientIDsToDB(aoOrthancStudyID)
-- 
--     if gSQLOpen then
--         if gSQLConn then
--             CloseSQL()
--         end
--     end
--     gSQLOpen = false
--     OpenSQL()
-- 
--     loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoOrthancStudyID, false))
--     aPatientIDModifier = ''
--     local lFlagNewPatientID, lSQLpid, ldPatientIDAnon = SavePatientIDsToDB(loStudyMeta,aPatientIDModifier)
--     local lPostData = {}
--     lPostData['OrthancStudyID'] = aoOrthancStudyID
--     lPostData['PatientIDModifier'] = aPatientIDModifier
--     local lResults
--     lResults = ParseJson(RestApiPost('/save_patient_ids_to_db_lua', DumpJson(lPostData), false))
--     PrintRecursive(lResults)
--     print(lResults['FlagPatientNewID'])
--     print(math.floor(lResults['SQLpid']+0.5))
--     print(lResults['PatientIDAnon'])
-- 
-- end
-- 
-- -- ======================================================
-- function SavePatientIDsToDB(aoStudyMeta,aPatientIDModifier)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     if not aoStudyMeta['PatientMainDicomTags'] then 
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Missing PatientMainDicomTags")
--     end
-- 
--     -- ConfirmLookupTablesSQL()
--     local lStatus = ParseJson(RestApiGet('/confirm_or_create_lookup_table_sql_lua', false, {['x-remote-user']='lua-ConfirmOrCreate'}))
--     if lStatus['error_text'] then
--         error(lStatus['error_text'])
--     end
-- 
--     local lPatientIDs = {}
--     local lPostData = {}
--     lPostData['OrthancStudyID'] = aoStudyMeta['ID']
--     if aPatientIDModifier then lPostData['PatientIDModifier'] = aPatientIDModifier end
--     -- lPatientIDs['dicom'] = GetPatientIDs(aoStudyMeta,aPatientIDModifier) 
--     local lResult = ParseJson(RestApiPost('/get_patient_ids_lua', DumpJson(lPostData), false, {['x-remote-user']='lua-get_patient_ids'}))
--     lPatientIDs['dicom'] = {}
--     for i, lIndex in ipairs(lResult['indices']) do
--         lPatientIDs['dicom'][lIndex] = lResult['patient_ids'][i]
--     end
--     if #lPatientIDs['dicom'] == 0 then 
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Missing DICOM PatientIDs")
--     end
-- 
--     -- Query database for any matches to dicom PatientID
--     local lSQLStatus, lSQLQuery, lSQLCursor, lSQLRow
--     lPatientIDs['pid'] = {}
--     lPatientIDs['map'] = {}
--     local j = 0
--     local k
--     for i, ldPatientID in ipairs(lPatientIDs['dicom']) do
--         k = 0
--         lSQLQuery = string.format(
--                 [[SELECT pid, parent_pid  
--                   FROM patientid  
--                   WHERE value='%s']], 
--                 gSQLConn:escape(ldPatientID))
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--         if not lSQLStatus then 
--             gSQLConn:rollback()
--             CloseSQL()
--             error("Problem querying pid, parent_pid")
--         end
--         lPatientIDs['map'][ldPatientID] = {}
--         if lSQLCursor:numrows() > 0 then
--             lSQLRow = lSQLCursor:fetch({}, "a")
--             while lSQLRow do
--                 j = j + 1
--                 k = k + 1
--                 if lSQLRow.parent_pid then
--                     lPatientIDs['pid'][j] = lSQLRow.parent_pid
--                 else
--                     lPatientIDs['pid'][j] = lSQLRow.pid
--                 end
--                 lPatientIDs['map'][ldPatientID][k] = lPatientIDs['pid'][j]
--                 lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--             end
--         end
--     end
-- 
--     -- If any are defined, there should only be one unique pid
--     local lSQLpidUnique = {}
--     local lFlagNewPatientID = (#lPatientIDs['pid'] == 0)
--     if not lFlagNewPatientID then
--         local lCheck = {}
--         j = 0
--         for i, lSQLpid in ipairs(lPatientIDs['pid']) do
--             if not lCheck[lSQLpid] then
--                 j = j + 1
--                 lSQLpidUnique[j] = lSQLpid
--                 lCheck[lSQLpid] = 1
--             end
--         end
--         if #lSQLpidUnique > 1 then
--             PrintRecursive(lSQLpidUnique)
--             gSQLConn:rollback()
--             CloseSQL()
--             error("More than one unique pid found")
--         end
--     end
-- 
--     -- Handle any new PatientIDs that match a previous one
--     if not lFlagNewPatientID then
--         --    To get here, lSQLpidUnique has only 1 element
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--         lSQLResult = gSQLConn:setautocommit(false)
--         for i, ldPatientID in ipairs(lPatientIDs['dicom']) do
--             if not lPatientIDs['map'][ldPatientID][1] then
--                 lSQLQuery = string.format(
--                               [[INSERT INTO patientid 
--                                 (value, parent_pid) 
--                                 VALUES('%s',%d)]],
--                               gSQLConn:escape(ldPatientID),
--                               lSQLpidUnique[1])
--                 lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--                 if not lSQLStatus then
--                     lSQLResult = gSQLConn:rollback()
--                     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--                     lSQLResult = gSQLConn:setautocommit(true)
--                     CloseSQL()
--                     error("Problem 1 inserting new patientid, parent_pid")
--                 end
--                 lPatientIDs['map'][ldPatientID][1] = lSQLpidUnique[1]
--                 if #lPatientIDs['map'][ldPatientID] > 1 then
--                     for j = 2, #lPatientIDs['map'][ldPatientID] do
--                         lPatientIDs['map'][ldPatientID][j] = nil
--                     end
--                 end
--             end
--         end
--         lSQLResult = gSQLConn:commit()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--     else -- Should only be here if this is a brand new patient
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--         lSQLResult = gSQLConn:setautocommit(false)
--         local lFirstLoop = true
--         for i, ldPatientID in ipairs(lPatientIDs['dicom']) do
--             if not lFirstLoop then
--                 lSQLQuery = string.format(
--                               [[INSERT INTO patientid
--                                 (value, parent_pid) 
--                                 VALUES('%s',%d)]],
--                               gSQLConn:escape(ldPatientID),
--                               lSQLpidUnique[1])
--                 lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--                 if not lSQLStatus then 
--                     lSQLResult = gSQLConn:rollback()
--                     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--                     lSQLResult = gSQLConn:setautocommit(true)
--                     CloseSQL()
--                     error("Problem 2 inserting new patientid, parent_pid")
--                 end
--             else
--                 lSQLQuery = string.format(
--                               [[INSERT INTO patientid (value) VALUES('%s')]],
--                               gSQLConn:escape(ldPatientID))
--                 lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--                 if not lSQLStatus then 
--                     lSQLResult = gSQLConn:rollback()
--                     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--                     lSQLResult = gSQLConn:setautocommit(true)
--                     CloseSQL()
--                     error("Problem inserting new patientid")
--                 end
--                 lSQLQuery = string.format(
--                         [[SELECT pid FROM patientid WHERE value='%s']], 
--                         gSQLConn:escape(ldPatientID))
--                 lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--                 if not lSQLStatus then 
--                     lSQLResult = gSQLConn:rollback()
--                     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--                     lSQLResult = gSQLConn:setautocommit(true)
--                     CloseSQL()
--                     error("Problem post-insert selecting new patientid")
--                 end
--                 lSQLRow = lSQLCursor:fetch({},"a")
--                 lPatientIDs['map'][ldPatientID][1] = lSQLRow.pid
--                 lSQLpidUnique[1] = lSQLRow.pid
--             end
--             lFirstLoop = false
--         end
--         lSQLResult = gSQLConn:commit()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--     end
-- 
--     -- Look for anonymized IDs for this lSQLpid
--     lSQLQuery = string.format(
--                    [[SELECT value FROM patientid_anon WHERE pid=%d]],
--                    lSQLpidUnique[1])
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem selecting from patientid_anon")
--     end
--     if lSQLCursor:numrows() > 1 then 
--         error("More than one corresponding patientid_anon")
--     end
--     local ldPatientIDAnon
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({},"a")
--         ldPatientIDAnon = lSQLRow.value
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lFlagNewPatientID, lSQLpidUnique[1], ldPatientIDAnon
-- 
-- end
-- 
-- ======================================================
-- function TestSaveStudyInstanceUIDToDB(aoOrthancStudyID)
-- 
--     if gSQLOpen then
--         if gSQLConn then
--             CloseSQL()
--         end
--     end
--     gSQLOpen = false
--     OpenSQL()
-- 
--     loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoOrthancStudyID, false))
--     aPatientIDModifier = ''
--     local lPostData = {}
--     lPostData['OrthancStudyID'] = loStudyMeta['ID']
--     if aPatientIDModifier then lPostData['PatientIDModifier'] = aPatientIDModifier end
--     local lResults
--     print('Calling save patient ids to db python')
--     lResults = ParseJson(RestApiPost('/save_patient_ids_to_db_lua', DumpJson(lPostData), false))
--     -- local lSQLpid = math.floor(lResults['SQLpid']+0.5)
--     local lSQLpid = lResults['SQLpid']
--     local lStudyInstanceUIDModifier = ''
--     print('Calling save studyinstanceuid to db native')
--     local lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon = SaveStudyInstanceUIDToDB(loStudyMeta,lSQLpid,lStudyInstanceUIDModifier)
--     print(lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon)
-- 
--     print('Calling save studyinstanceuid to db python')
--     lPostData = {}
--     lPostData['OrthancStudyID'] = loStudyMeta['ID']
--     lPostData['SQLpid'] = lSQLpid
--     local lResults
--     lResults = ParseJson(RestApiPost('/save_study_instance_uid_to_db_lua', DumpJson(lPostData), false))
--     PrintRecursive(lResults)   
--     print('done')
--     
-- end
-- 
-- -- ======================================================
-- function SaveStudyInstanceUIDToDB(aoStudyMeta,aSQLpid,aStudyInstanceUIDModifier)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     -- Missing data handling
--     local lSQLsiuid, ldStudyInstanceUIDAnon
--     if not aoStudyMeta['MainDicomTags'] then 
--         error("Missing MainDicomTags")
--     end
--     if not aoStudyMeta['MainDicomTags']['StudyInstanceUID'] then
--         error('No StudyInstanceUID')
--     end
--     local ldStudyInstanceUID = aoStudyMeta['MainDicomTags']['StudyInstanceUID']
--     if not ldStudyInstanceUID then
--         error("Missing StudyInstanceUID")
--     end
--     ldStudyInstanceUID = ldStudyInstanceUID .. aStudyInstanceUIDModifier
-- 
--     -- Check for StudyInstanceUID in DB
--     local lSQLCursor, lSQLStatus
--     local lSQLQuery = string.format(
--                         [[SELECT * FROM studyinstanceuid WHERE value='%s']],
--                         gSQLConn:escape(ldStudyInstanceUID))
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         CloseSQL()
--         error("Probling finding studyinstanceuid")
--     end
--     local lNRows = lSQLCursor:numrows()
--     if lNRows > 1 then
--         error("More than one occurrence of studyinstanceuid in db")
--     end
--     if lNRows > 0 then
--         local lSQLRow = lSQLCursor:fetch({}, "a")
--         if lSQLRow.pid ~= aSQLpid then
--             print(type(lSQLRow.pid), type(aSQLpid))
--             error("DB pid " .. lSQLRow.pid .. " for StudyInstanceUID does not match PatientID pid " .. aSQLpid)
--         end
--         lSQLsiuid = lSQLRow.siuid
--     end
-- 
--     -- Check for anonymized studies
--     local lFlagNewStudyInstanceUID
--     if lSQLsiuid then
--         lFlagNewStudyInstanceUID = false
--         lSQLQuery = string.format(
--                         [[SELECT value 
--                           FROM studyinstanceuid_anon 
--                           WHERE siuid = %d]], lSQLsiuid)
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--         if not lSQLStatus then
--             CloseSQL()
--             error("Probling finding studyinstanceuid_anon")
--         end
--         local lNRows = lSQLCursor:numrows()
--         if lNRows > 1 then
--             error("More than one occurrence of studyinstanceuid_anon in db")
--         end
--         if lNRows > 0 then
--             local lSQLRow = lSQLCursor:fetch({}, "a")
--             ldStudyInstanceUIDAnon = lSQLRow.value
--         end
--     -- Else insert a brand new study
--     else
--         lFlagNewStudyInstanceUID = true
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--         lSQLCursor = gSQLConn:setautocommit(false)
--         lSQLQuery = string.format(
--                         [[INSERT INTO studyinstanceuid (value,pid)
--                           VALUES('%s',%d)]], 
--                           gSQLConn:escape(ldStudyInstanceUID), aSQLpid)
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--         if not lSQLStatus then
--             lSQLCursor = gSQLConn:rollback()
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--             lSQLCursor = gSQLConn:setautocommit(true)
--             CloseSQL()
--             error("Problem inserting studyinstanceuid, pid")
--         end
--         lSQLQuery = string.format(
--                         [[SELECT siuid FROM studyinstanceuid
--                           WHERE value='%s']], gSQLConn:escape(ldStudyInstanceUID))
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--         if not lSQLStatus then
--             lSQLCursor = gSQLConn:rollback()
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--             lSQLCursor = gSQLConn:setautocommit(true)
--             CloseSQL()
--             error("Problem post-insert selecting studyinstanceuid, pid")
--         end
--         local lSQLRow = lSQLCursor:fetch({}, "a")
--         lSQLsiuid = lSQLRow.siuid
--         lSQLCursor = gSQLConn:commit()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLCursor = gSQLConn:setautocommit(true)
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon
-- 
-- end
-- 
-- -- ======================================================
-- function GetInternalNumber(aSQLpid, aPatientIDModifier)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lInternalNumber
--     local lSQLQuery = string.format([[SELECT value FROM internalnumber WHERE pid=%d]],aSQLpid)
--     local lSQLStatus, lSQLCursor
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then 
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Problem selecting internalnumber")
--     end
--     -- We found one already created
--     local lSQLRow
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         lInternalNumber = lSQLRow.value
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--         gIndent = gIndent - 3
--         if gIndent > 0 then gIndent = gIndent - 3 end
--         return lInternalNumber
--     end
-- 
--     -- We need to generate one
--     if not lInternalNumber then
--         
--         -- Find an internal number already not in use
--         local lInternalNumberNew
--         local lInternalNumberType = os.getenv('LUA_INTERNAL_NUMBER_TYPE')
--         if lInternalNumberType == 'random' then
--             while not lInternalNumber do
--                 lInternalNumberNew = math.random(1,999999)
--                 lSQLQuery = string.format([[SELECT count(*) FROM internalnumber WHERE value=%d]],lInternalNumberNew)
--                 lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--                 if not lSQLStatus then 
--                     gSQLConn:rollback()
--                     CloseSQL()
--                     error("Problem selecting internalnumber value")
--                 end
--                 lSQLRow = lSQLCursor:fetch({},"a")
--                 if tonumber(lSQLRow.count) == 0 then
--                     lInternalNumber = lInternalNumberNew
--                 end
--             end
--         elseif lInternalNumberType == 'monotonic' then
--             lInternalNumberNew = 0
--             while not lInternalNumber do
--                 lInternalNumberNew = lInternalNumberNew + 1
--                 lSQLQuery = string.format([[SELECT count(*) FROM internalnumber WHERE value=%d]],lInternalNumberNew)
--                 lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--                 if not lSQLStatus then 
--                     gSQLConn:rollback()
--                     CloseSQL()
--                     error("Problem selecting internalnumber value")
--                 end
--                 lSQLRow = lSQLCursor:fetch({},"a")
--                 if tonumber(lSQLRow.count) == 0 then
--                     lInternalNumber = lInternalNumberNew
--                 end
--             end
--         elseif lInternalNumberType == 'winkler' then
--             local lInternalNumberOffset = 1000
--             if (aPatientIDModifier == 's') or (aPatientIDModifier == '2d') then
--                 lInternalNumberNew = 0
--             else
--                 lInternalNumberNew = lInternalNumberOffset
--             end
--             while not lInternalNumber do
--                 lInternalNumberNew = lInternalNumberNew + 1
--                 if (lInternalNumberNew % lInternalNumberOffset) == 0 then
--                     lInternalNumberNew = lInternalNumberNew + lInternalNumberOffset + 1;
--                 end
--                 lSQLQuery = string.format([[SELECT count(*) FROM internalnumber WHERE value=%d]],lInternalNumberNew)
--                 lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--                 if not lSQLStatus then 
--                     gSQLConn:rollback()
--                     CloseSQL()
--                     error("Problem selecting internalnumber value")
--                 end
--                 lSQLRow = lSQLCursor:fetch({},"a")
--                 if tonumber(lSQLRow.count) == 0 then
--                     lInternalNumber = lInternalNumberNew
--                 end
--             end
--         else -- default same as incoming aSQLpid
--             lInternalNumber = aSQLpid
--         end
-- 
--         -- Store the internal number
--         lSQLQuery = string.format([[INSERT INTO internalnumber (value,pid) VALUES(%d,%d)]], lInternalNumber, aSQLpid)
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--         lSQLResult = gSQLConn:setautocommit(false)
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--         if not lSQLStatus then
--             lSQLResult = gSQLConn:rollback()
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--             lSQLResult = gSQLConn:setautocommit(true)
--             CloseSQL()
--             error("Problem inserting internalnumber")
--         end
--         lSQLResult = gSQLConn:commit()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
-- 
--     end -- endif we started with no pre-existing internalnumber
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lInternalNumber
-- 
-- end
--
-- ======================================================
-- function ConstructPatientName(aInteger)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     local lPatientNameBase
--     if not gPatientNameBase then
--         local loSystemMeta = ParseJson(RestApiGet('/system', false))
--         lPatientNameBase = loSystemMeta['Name']
--     else
--         lPatientNameBase = gPatientNameBase
--     end
--     local lPatientNameIDChar
--     if gPatientNameIDChar then
--         lPatientNameIDChar = gPatientNameIDChar
--     else
--         lPatientNameIDChar = 'ID'
--     end
--     local lPatientName = string.format('%s^%s%06d^^^', lPatientNameBase, lPatientNameIDChar, aInteger)
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPatientName
-- 
-- end
-- 
-- ======================================================
-- function SavePatientIDsAnonToDB(aoStudyMeta,aSQLpid)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     if not aoStudyMeta['PatientMainDicomTags'] then 
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Missing PatientMainDicomTags")
--     end
-- 
--     local ldPatientID = aoStudyMeta['PatientMainDicomTags']['PatientID']
--     if not ldPatientID then
--         gSQLConn:rollback()
--         CloseSQL()
--         error('No PatientID')
--     end
-- 
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--     local lSQLResult = gSQLConn:setautocommit(false)
--     local lSQLQuery = string.format(
--                         [[INSERT INTO patientid_anon (value,pid)
--                           VALUES('%s',%d)]], 
--                           gSQLConn:escape(ldPatientID), aSQLpid)
--     local lSQLStatus, lSQLCursor
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem inserting patientid_anon")
--     end
--     lSQLResult = gSQLConn:commit()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--     lSQLResult = gSQLConn:setautocommit(true)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- ======================================================
-- function SaveStudyInstanceUIDAnonToDB(aoStudyMeta,aSQLsiuid)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local ldStudyInstanceUID = aoStudyMeta['MainDicomTags']['StudyInstanceUID']
--     if not ldStudyInstanceUID then
--         gSQLConn:rollback()
--         CloseSQL()
--         error("Missing StudyInstanceUID")
--     end
-- 
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--     local lSQLResult = gSQLConn:setautocommit(false)
--     local lSQLQuery = string.format(
--                         [[INSERT INTO studyinstanceuid_anon
--                           (value,siuid)
--                           VALUES('%s',%d)]],
--                           gSQLConn:escape(ldStudyInstanceUID),aSQLsiuid)
--     local lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem inserting studyinstanceuid_anon")
--     end
--     lSQLResult = gSQLConn:commit()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--     local lSQLResult = gSQLConn:setautocommit(true)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- ======================================================
-- function SavePatientNameAnonToDB(aPatientName,aSQLsiuid)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     gIndent = gIndent + 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'PatientNameAnon ' .. aPatientName) end
--     local lTime0 = os.time()
--     local lTimeStamp = os.date("%Y-%m-%d %H:%M:%S",lTime0)
-- 
--     local lSQLQuery = [[SELECT table_name 
--                        FROM information_schema.tables 
--                        WHERE table_name='siuid2patientname_anon']]
--     local lSQLStatus, lSQLCursor
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then
--         if gVerbose then print(string.rep(' ',gIndent) .. 'siuid2patientname_anon does not exist.  Skipping...') end
--         return
--     end
-- 
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--     local lSQLResult = gSQLConn:setautocommit(false)
-- 
--     lSQLQuery = string.format(
--                   [[INSERT INTO siuid2patientname_anon 
--                     (patientname_anon, timestamp, siuid) 
--                     VALUES ('%s', '%s', %d)]], 
--                     gSQLConn:escape(aPatientName),gSQLConn:escape(lTimeStamp), aSQLsiuid)
--     lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem inserting patientname_anon: " .. lSQLQuery)
--     end
--     lSQLResult = gSQLConn:commit()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--     local lSQLResult = gSQLConn:setautocommit(true)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- ======================================================
-- function TestRecursiveFindUID()
-- 
--     gTopLevelTagToKeep = {}
--     gKeptUID = {}
--     local orthanc_instance_id = 'acd0cdfa-51944655-fb72c173-9c02d9b3-12863225'
--     local loLevelInstanceMeta = ParseJson(RestApiGet('/instances/' .. orthanc_instance_id .. '/tags', false))
--     -- PrintRecursive(loLevelInstanceMeta)
--     RecursiveFindUIDToKeep(loLevelInstanceMeta)
--     PrintRecursive(gKeptUID)
--     PrintRecursive(gTopLevelTagToKeep)
-- 
--     local lResult = ParseJson(RestApiGet('/instances/' .. orthanc_instance_id .. '/recursive_find_uid_to_keep_lua', false))
--     if lResult['status'] > 0 then
--         error(lResult['error_text'])
--     end
--     gTopLevelTagToKeep = lResult['TopLevelTagToKeep']
--     gKeptUID = lResult['KeptUID']
--     PrintRecursive(gKeptUID)
--     PrintRecursive(gTopLevelTagToKeep)
-- 
-- end
--     
-- -- ======================================================
-- function RecursiveFindUIDToKeep(aParent, aLevelIn)
-- 
--     gMaxRecurseDepth = 20
--     local lLevelIn = (aLevelIn) or gMaxRecurseDepth
--     local lLevelOut = lLevelIn - 1
--     if (lLevelIn<1) then return lLevelOut end;
--     local lParentType = type(aParent);
--     if (lParentType ~= "table") then return lLevelOut end
--     for k,lChild in pairs(aParent) do  
--         if lChild['Name'] then
--             if (type(lChild['Value']) == "table") and (lLevelIn == gMaxRecurseDepth) then 
--                 gParentTag=k
--             end
--             if string.find(lChild['Name'],'UID') and lChild['Value'] then
--                 gKeptUID[lChild['Value']] = {}
--                 gKeptUID[lChild['Value']]['Numeric'] = k
--                 gKeptUID[lChild['Value']]['Name'] = lChild['Name']
--                 if lLevelIn < gMaxRecurseDepth then 
--                     gTopLevelTagToKeep[gParentTag] = true
--                 end
--                 if (lLevelIn == gMaxRecurseDepth) and 
--                    (not (lChild['Name'] == 'StudyInstanceUID')) and 
--                    (not (lChild['Name'] == 'SeriesInstanceUID')) and
--                    (not (lChild['Name'] == 'SOPInstanceUID')) then
--                    gTopLevelTagToKeep[k] = true
--                 end
--             end
--             lLevelOut = RecursiveFindUIDToKeep(lChild['Value'], lLevelIn-1);
--             if (type(lChild['Value']) == "table") and (lLevelIn == gMaxRecurseDepth) then 
--                 gParentTag = nil
--             end
--         else
--             lLevelOut = RecursiveFindUIDToKeep(lChild, lLevelIn-1);
--         end
--         if (lLevelOut < 0) then break end
--     end
--     return lLevelOut
-- 
-- end    
-- 
-- ======================================================
function BaseTagHandling ()

    local lFlagKeepSiemensMR = os.getenv('LUA_FLAG_KEEP_SIEMENS_MR_TAGS') == 'true'
    local lFlagHologic = os.getenv('LUA_COLLECT_HOLOGIC') == 'true'

    local lTableFromCTP
    lTableFromCTP = {}
    lTableFromCTP['0008-0005'] = {en = true,  op = 'keep',    name = 'SpecificCharacterSet',                         comment = ''}
    lTableFromCTP['0008-0008'] = {en = true,  op = 'keep',    name = 'ImageType',                                    comment = ''}
    lTableFromCTP['0008-0012'] = {en = true,  op = 'keep',    name = 'InstanceCreationDate',                         comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0013'] = {en = true,  op = 'keep',    name = 'InstanceCreationTime',                         comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0014'] = {en = true,  op = 'remove',  name = 'InstanceCreatorUID',                           comment = ''}
    lTableFromCTP['0008-0016'] = {en = true,  op = 'keep',    name = 'SOPClassUID',                                  comment = 'In general this is not PHI'}
    lTableFromCTP['0008-0018'] = {en = true,  op = 'orthanc', name = 'SOPInstanceUID',                               comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0008-0020'] = {en = true,  op = 'keep',    name = 'StudyDate',                                    comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0021'] = {en = true,  op = 'keep',    name = 'SeriesDate',                                   comment = ''}
    lTableFromCTP['0008-0022'] = {en = true,  op = 'keep',    name = 'AcquisitionDate',                              comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0023'] = {en = true,  op = 'keep',    name = 'ContentDate',                                  comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0024'] = {en = true,  op = 'remove',  name = 'OverlayDate',                                  comment = ''}
    lTableFromCTP['0008-0025'] = {en = true,  op = 'remove',  name = 'CurveDate',                                    comment = ''}
    lTableFromCTP['0008-002a'] = {en = true,  op = 'keep',    name = 'AcquisitionDateTime',                          comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0030'] = {en = true,  op = 'keep',    name = 'StudyTime',                                    comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0031'] = {en = true,  op = 'keep',    name = 'SeriesTime',                                   comment = ''}
    lTableFromCTP['0008-0032'] = {en = true,  op = 'keep',    name = 'AcquisitionTime',                              comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0033'] = {en = true,  op = 'keep',    name = 'ContentTime',                                  comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0008-0034'] = {en = true,  op = 'remove',  name = 'OverlayTime',                                  comment = ''}
    lTableFromCTP['0008-0035'] = {en = true,  op = 'remove',  name = 'CurveTime',                                    comment = ''}
    lTableFromCTP['0008-0050'] = {en = true,  op = 'keep',    name = 'AccessionNumber',                              comment = 'Orthanc will replace this'}
    lTableFromCTP['0008-0052'] = {en = false, op = '',        name = 'QueryRetrieveLevel',                           comment = ''}
    lTableFromCTP['0008-0054'] = {en = false, op = '',        name = 'RetrieveAET',                                  comment = ''}
    lTableFromCTP['0008-0056'] = {en = false, op = '',        name = 'InstanceAvailability',                         comment = ''}
    lTableFromCTP['0008-0058'] = {en = false, op = '',        name = 'FailedSOPInstanceUIDList',                     comment = ''}
    lTableFromCTP['0008-0060'] = {en = true,  op = 'keep',    name = 'Modality',                                     comment = ''}
    lTableFromCTP['0008-0061'] = {en = true,  op = 'keep',    name = 'ModalitiesInStudy',                            comment = ''}
    lTableFromCTP['0008-0064'] = {en = false, op = '',        name = 'ConversionType',                               comment = ''}
    lTableFromCTP['0008-0068'] = {en = false, op = '',        name = 'PresentationIntentType',                       comment = ''}
    lTableFromCTP['0008-0070'] = {en = true,  op = 'keep',    name = 'Manufacturer',                                 comment = 'We typically keeps this'}
    lTableFromCTP['0008-0080'] = {en = true,  op = 'remove',  name = 'InstitutionName',                              comment = ''}
    lTableFromCTP['0008-0081'] = {en = true,  op = 'remove',  name = 'InstitutionAddress',                           comment = ''}
    lTableFromCTP['0008-0082'] = {en = true,  op = 'remove',  name = 'InstitutionCodeSeq',                           comment = ''}
    lTableFromCTP['0008-0090'] = {en = true,  op = 'empty',   name = 'ReferringPhysicianName',                       comment = ''}
    lTableFromCTP['0008-0092'] = {en = true,  op = 'remove',  name = 'ReferringPhysicianAddress',                    comment = ''}
    lTableFromCTP['0008-0094'] = {en = true,  op = 'remove',  name = 'ReferringPhysicianPhoneNumbers',               comment = ''}
    lTableFromCTP['0008-0096'] = {en = true,  op = 'remove',  name = 'ReferringPhysiciansIDSeq',                     comment = ''}
    lTableFromCTP['0008-0100'] = {en = false, op = '',        name = 'CodeValue',                                    comment = ''}
    lTableFromCTP['0008-0102'] = {en = false, op = '',        name = 'CodingSchemeDesignator',                       comment = ''}
    lTableFromCTP['0008-0103'] = {en = false, op = '',        name = 'CodingSchemeVersion',                          comment = ''}
    lTableFromCTP['0008-0104'] = {en = false, op = '',        name = 'CodeMeaning',                                  comment = ''}
    lTableFromCTP['0008-0105'] = {en = false, op = '',        name = 'MappingResource',                              comment = ''}
    lTableFromCTP['0008-0106'] = {en = false, op = '',        name = 'ContextGroupVersion',                          comment = ''}
    lTableFromCTP['0008-0107'] = {en = false, op = '',        name = 'ContextGroupLocalVersion',                     comment = ''}
    lTableFromCTP['0008-010b'] = {en = false, op = '',        name = 'CodeSetExtensionFlag',                         comment = ''}
    lTableFromCTP['0008-010c'] = {en = true,  op = 'remove',  name = 'PrivateCodingSchemeCreatorUID',                comment = ''}
    lTableFromCTP['0008-010d'] = {en = true,  op = 'remove',  name = 'CodeSetExtensionCreatorUID',                   comment = ''}
    lTableFromCTP['0008-010f'] = {en = false, op = '',        name = 'ContextIdentifier',                            comment = ''}
    lTableFromCTP['0008-0201'] = {en = true,  op = 'remove',  name = 'TimezoneOffsetFromUTC',                        comment = ''}
    lTableFromCTP['0008-1010'] = {en = true,  op = 'remove',  name = 'StationName',                                  comment = 'Some groups want to keep this'}
    lTableFromCTP['0008-1030'] = {en = true,  op = 'keep',    name = 'StudyDescription',                             comment = 'We tends to keep this'}
    if lFlagHologic then
        lTableFromCTP['0008-1032']={en = true, op = 'keep',   name = 'ProcedureCodeSeq',                             comment = 'Winkler needs to keep this for Hologic'}
    else
        lTableFromCTP['0008-1032']={en = true, op = 'remove', name = 'ProcedureCodeSeq',                             comment = 'Winkler needs to keep this for Hologic'}
    end
    lTableFromCTP['0008-103e'] = {en = true,  op = 'keep',    name = 'SeriesDescription',                            comment = 'We tends to keep this'}
    lTableFromCTP['0008-1040'] = {en = true,  op = 'remove',  name = 'InstitutionalDepartmentName',                  comment = ''}
    lTableFromCTP['0008-1048'] = {en = true,  op = 'remove',  name = 'PhysicianOfRecord',                            comment = ''}
    lTableFromCTP['0008-1049'] = {en = true,  op = 'remove',  name = 'PhysicianOfRecordIdSeq',                       comment = ''}
    lTableFromCTP['0008-1050'] = {en = true,  op = 'remove',  name = 'PerformingPhysicianName',                      comment = ''}
    lTableFromCTP['0008-1052'] = {en = true,  op = 'remove',  name = 'PerformingPhysicianIdSeq',                     comment = ''}
    lTableFromCTP['0008-1060'] = {en = true,  op = 'remove',  name = 'NameOfPhysicianReadingStudy',                  comment = ''}
    lTableFromCTP['0008-1062'] = {en = true,  op = 'remove',  name = 'PhysicianReadingStudyIdSeq',                   comment = ''}
    lTableFromCTP['0008-1070'] = {en = true,  op = 'remove',  name = 'OperatorName',                                 comment = ''}
    lTableFromCTP['0008-1072'] = {en = true,  op = 'remove',  name = 'OperatorsIdentificationSeq',                   comment = ''}
    lTableFromCTP['0008-1080'] = {en = true,  op = 'remove',  name = 'AdmittingDiagnosisDescription',                comment = ''}
    lTableFromCTP['0008-1084'] = {en = true,  op = 'remove',  name = 'AdmittingDiagnosisCodeSeq',                    comment = ''}
    lTableFromCTP['0008-1090'] = {en = true,  op = 'keep',    name = 'ManufacturerModelName',                        comment = 'Some groups (Cardiac) like to keep this'}
    lTableFromCTP['0008-1100'] = {en = false, op = '',        name = 'RefResultsSeq',                                comment = ''}
    lTableFromCTP['0008-1110'] = {en = true,  op = 'remove',  name = 'RefStudySeq',                                  comment = ''}
    lTableFromCTP['0008-1111'] = {en = true,  op = 'remove',  name = 'RefPPSSeq',                                    comment = ''}
    lTableFromCTP['0008-1115'] = {en = false, op = '',        name = 'RefSeriesSeq',                                 comment = ''}
    lTableFromCTP['0008-1120'] = {en = true,  op = 'remove',  name = 'RefPatientSeq',                                comment = ''}
    lTableFromCTP['0008-1125'] = {en = false, op = '',        name = 'RefVisitSeq',                                  comment = ''}
    lTableFromCTP['0008-1130'] = {en = false, op = '',        name = 'RefOverlaySeq',                                comment = ''}
    lTableFromCTP['0008-1140'] = {en = true,  op = 'orthanc', name = 'RefImageSeq',                                  comment = ''}
    lTableFromCTP['0008-1145'] = {en = false, op = '',        name = 'RefCurveSeq',                                  comment = ''}
    lTableFromCTP['0008-114a'] = {en = false, op = '',        name = 'RefInstanceSeq',                               comment = ''}
    lTableFromCTP['0008-1150'] = {en = true,  op = 'orthanc', name = 'RefSOPClassUID',                               comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0008-1155'] = {en = true,  op = 'orthanc', name = 'RefSOPInstanceUID',                            comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0008-115a'] = {en = false, op = '',        name = 'SOPClassesSupported',                          comment = ''}
    lTableFromCTP['0008-1160'] = {en = false, op = '',        name = 'RefFrameNumber',                               comment = ''}
    lTableFromCTP['0008-1195'] = {en = true,  op = 'remove',  name = 'TransactionUID',                               comment = ''}
    lTableFromCTP['0008-1197'] = {en = false, op = '',        name = 'FailureReason',                                comment = ''}
    lTableFromCTP['0008-1198'] = {en = false, op = '',        name = 'FailedSOPSeq',                                 comment = ''}
    lTableFromCTP['0008-1199'] = {en = false, op = '',        name = 'RefSOPSeq',                                    comment = ''}
    lTableFromCTP['0008-2111'] = {en = true,  op = 'remove',  name = 'DerivationDescription',                        comment = ''}
    lTableFromCTP['0008-2112'] = {en = true,  op = 'remove',  name = 'SourceImageSeq',                               comment = ''}
    lTableFromCTP['0008-2120'] = {en = false, op = '',        name = 'StageName',                                    comment = ''}
    lTableFromCTP['0008-2122'] = {en = false, op = '',        name = 'StageNumber',                                  comment = ''}
    lTableFromCTP['0008-2124'] = {en = false, op = '',        name = 'NumberOfStages',                               comment = ''}
    lTableFromCTP['0008-2128'] = {en = false, op = '',        name = 'ViewNumber',                                   comment = ''}
    lTableFromCTP['0008-2129'] = {en = false, op = '',        name = 'NumberOfEventTimers',                          comment = ''}
    lTableFromCTP['0008-212a'] = {en = false, op = '',        name = 'NumberOfViewsInStage',                         comment = ''}
    lTableFromCTP['0008-2130'] = {en = false, op = '',        name = 'EventElapsedTime',                             comment = ''}
    lTableFromCTP['0008-2132'] = {en = false, op = '',        name = 'EventTimerName',                               comment = ''}
    lTableFromCTP['0008-2142'] = {en = false, op = '',        name = 'StartTrim',                                    comment = ''}
    lTableFromCTP['0008-2143'] = {en = false, op = '',        name = 'StopTrim',                                     comment = ''}
    lTableFromCTP['0008-2144'] = {en = false, op = '',        name = 'RecommendedDisplayFrameRate',                  comment = ''}
    lTableFromCTP['0008-2218'] = {en = false, op = '',        name = 'AnatomicRegionSeq',                            comment = ''}
    lTableFromCTP['0008-2220'] = {en = false, op = '',        name = 'AnatomicRegionModifierSeq',                    comment = ''}
    lTableFromCTP['0008-2228'] = {en = false, op = '',        name = 'PrimaryAnatomicStructureSeq',                  comment = ''}
    lTableFromCTP['0008-2229'] = {en = false, op = '',        name = 'AnatomicStructureSpaceRegionSeq',              comment = ''}
    lTableFromCTP['0008-2230'] = {en = false, op = '',        name = 'PrimaryAnatomicStructureModifierSeq',          comment = ''}
    lTableFromCTP['0008-2240'] = {en = false, op = '',        name = 'TransducerPositionSeq',                        comment = ''}
    lTableFromCTP['0008-2242'] = {en = false, op = '',        name = 'TransducerPositionModifierSeq',                comment = ''}
    lTableFromCTP['0008-2244'] = {en = false, op = '',        name = 'TransducerOrientationSeq',                     comment = ''}
    lTableFromCTP['0008-2246'] = {en = false, op = '',        name = 'TransducerOrientationModifierSeq',             comment = ''}
    lTableFromCTP['0008-3010'] = {en = true,  op = 'remove',  name = 'IrradiationEventUID',                          comment = ''}
    lTableFromCTP['0008-4000'] = {en = true,  op = 'remove',  name = 'IdentifyingComments',                          comment = ''}
    lTableFromCTP['0008-9007'] = {en = false, op = '',        name = 'FrameType',                                    comment = ''}
    lTableFromCTP['0008-9092'] = {en = false, op = '',        name = 'ReferringImageEvidenceSeq',                    comment = ''}
    lTableFromCTP['0008-9121'] = {en = false, op = '',        name = 'RefRawDataSeq',                                comment = ''}
    lTableFromCTP['0008-9123'] = {en = true,  op = 'remove',  name = 'CreatorVersionUID',                            comment = ''}
    lTableFromCTP['0008-9124'] = {en = false, op = '',        name = 'DerivationImageSeq',                           comment = ''}
    lTableFromCTP['0008-9154'] = {en = false, op = '',        name = 'SourceImageEvidenceSeq',                       comment = ''}
    lTableFromCTP['0008-9205'] = {en = false, op = '',        name = 'PixelPresentation',                            comment = ''}
    lTableFromCTP['0008-9206'] = {en = false, op = '',        name = 'VolumetricProperties',                         comment = ''}
    lTableFromCTP['0008-9207'] = {en = false, op = '',        name = 'VolumeBasedCalculationTechnique',              comment = ''}
    lTableFromCTP['0008-9208'] = {en = false, op = '',        name = 'ComplexImageComponent',                        comment = ''}
    lTableFromCTP['0008-9209'] = {en = false, op = '',        name = 'AcquisitionContrast',                          comment = ''}
    lTableFromCTP['0008-9215'] = {en = false, op = '',        name = 'DerivationCodeSeq',                            comment = ''}
    lTableFromCTP['0008-9237'] = {en = false, op = '',        name = 'RefGrayscalePresentationStateSeq',             comment = ''}
    lTableFromCTP['0010-0021'] = {en = true,  op = 'remove',  name = 'IssuerOfPatientID',                            comment = ''}
    lTableFromCTP['0010-0030'] = {en = true,  op = 'keep',    name = 'PatientBirthDate',                             comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0010-0032'] = {en = true,  op = 'remove',  name = 'PatientBirthTime',                             comment = ''}
    lTableFromCTP['0010-0040'] = {en = true,  op = 'keep',    name = 'PatientSex',                                   comment = 'We keep this'}
    lTableFromCTP['0010-0050'] = {en = true,  op = 'remove',  name = 'PatientInsurancePlanCodeSeq',                  comment = ''}
    lTableFromCTP['0010-0101'] = {en = true,  op = 'remove',  name = 'PatientPrimaryLanguageCodeSeq',                comment = ''}
    lTableFromCTP['0010-0102'] = {en = true,  op = 'remove',  name = 'PatientPrimaryLanguageModifierCodeSeq',        comment = ''}
    lTableFromCTP['0010-1000'] = {en = true,  op = 'remove',  name = 'OtherPatientIDs',                              comment = ''}
    lTableFromCTP['0010-1001'] = {en = true,  op = 'remove',  name = 'OtherPatientNames',                            comment = ''}
    lTableFromCTP['0010-1002'] = {en = true,  op = 'remove',  name = 'OtherPatientIDsSeq',                           comment = ''}
    lTableFromCTP['0010-1005'] = {en = true,  op = 'remove',  name = 'PatientBirthName',                             comment = ''}
    lTableFromCTP['0010-1010'] = {en = true,  op = 'keep',    name = 'PatientAge',                                   comment = 'We keep this when shifting dates, otherwise remove'}
    lTableFromCTP['0010-1020'] = {en = true,  op = 'remove',  name = 'PatientSize',                                  comment = ''}
    lTableFromCTP['0010-1030'] = {en = true,  op = 'keep',    name = 'PatientWeight',                                comment = ''}
    lTableFromCTP['0010-1040'] = {en = true,  op = 'remove',  name = 'PatientAddress',                               comment = ''}
    lTableFromCTP['0010-1050'] = {en = true,  op = 'remove',  name = 'InsurancePlanIdentification',                  comment = ''}
    lTableFromCTP['0010-1060'] = {en = true,  op = 'remove',  name = 'PatientMotherBirthName',                       comment = ''}
    lTableFromCTP['0010-1080'] = {en = true,  op = 'remove',  name = 'MilitaryRank',                                 comment = ''}
    lTableFromCTP['0010-1081'] = {en = true,  op = 'remove',  name = 'BranchOfService',                              comment = ''}
    lTableFromCTP['0010-1090'] = {en = true,  op = 'remove',  name = 'MedicalRecordLocator',                         comment = ''}
    lTableFromCTP['0010-2000'] = {en = true,  op = 'remove',  name = 'MedicalAlerts',                                comment = ''}
    lTableFromCTP['0010-2110'] = {en = true,  op = 'remove',  name = 'ContrastAllergies',                            comment = ''}
    lTableFromCTP['0010-2150'] = {en = true,  op = 'remove',  name = 'CountryOfResidence',                           comment = ''}
    lTableFromCTP['0010-2152'] = {en = true,  op = 'remove',  name = 'RegionOfResidence',                            comment = ''}
    lTableFromCTP['0010-2154'] = {en = true,  op = 'remove',  name = 'PatientPhoneNumbers',                          comment = ''}
    lTableFromCTP['0010-2160'] = {en = true,  op = 'remove',  name = 'EthnicGroup',                                  comment = ''}
    lTableFromCTP['0010-2180'] = {en = true,  op = 'remove',  name = 'Occupation',                                   comment = ''}
    lTableFromCTP['0010-21a0'] = {en = true,  op = 'remove',  name = 'SmokingStatus',                                comment = ''}
    lTableFromCTP['0010-21b0'] = {en = true,  op = 'remove',  name = 'AdditionalPatientHistory',                     comment = ''}
    lTableFromCTP['0010-21c0'] = {en = true,  op = 'remove',  name = 'PregnancyStatus',                              comment = ''}
    lTableFromCTP['0010-21d0'] = {en = true,  op = 'remove',  name = 'LastMenstrualDate',                            comment = ''}
    lTableFromCTP['0010-21f0'] = {en = true,  op = 'remove',  name = 'PatientReligiousPreference',                   comment = ''}
    lTableFromCTP['0010-2203'] = {en = true,  op = 'remove',  name = 'PatientSexNeutered',                           comment = ''}
    lTableFromCTP['0010-2297'] = {en = true,  op = 'remove',  name = 'ResponsiblePerson',                            comment = ''}
    lTableFromCTP['0010-2299'] = {en = true,  op = 'remove',  name = 'ResponsibleOrganization',                      comment = ''}
    lTableFromCTP['0010-4000'] = {en = true,  op = 'remove',  name = 'PatientComments',                              comment = ''}
    lTableFromCTP['0012-0010'] = {en = false, op = 'fill',    name = 'ClinicalTrialSponsorName',                     comment = ''}
    lTableFromCTP['0012-0020'] = {en = false, op = '',        name = 'ClinicalTrialProtocolID',                      comment = ''}
    lTableFromCTP['0012-0021'] = {en = false, op = '',        name = 'ClinicalTrialProtocolName',                    comment = ''}
    lTableFromCTP['0012-0030'] = {en = false, op = 'fill',    name = 'ClinicalTrialSiteID',                          comment = ''}
    lTableFromCTP['0012-0031'] = {en = false, op = 'fill',    name = 'ClinicalTrialSiteName',                        comment = ''}
    lTableFromCTP['0012-0040'] = {en = false, op = 'fill',    name = 'ClinicalTrialSubjectID',                       comment = ''}
    lTableFromCTP['0012-0042'] = {en = false, op = '',        name = 'ClinicalTrialSubjectReadingID',                comment = ''}
    lTableFromCTP['0012-0050'] = {en = false, op = '',        name = 'ClinicalTrialTimePointID',                     comment = ''}
    lTableFromCTP['0012-0051'] = {en = false, op = '',        name = 'ClinicalTrialTimePointDescription',            comment = ''}
    lTableFromCTP['0012-0060'] = {en = false, op = '',        name = 'CoordinatingCenterName',                       comment = ''}
    lTableFromCTP['0012-0062'] = {en = true,  op = 'keep',    name = 'PatientIdentityRemoved',                       comment = 'Need to keep and-or update'}
    lTableFromCTP['0012-0063'] = {en = true,  op = 'keep',    name = 'DeidentificationMethod',                       comment = 'Need to fill this with some descriptor'}
    lTableFromCTP['0012-0064'] = {en = true,  op = 'keep',    name = 'DeidentificationMethodCodeSeq',                comment = 'May need to fill this if 12-63 not filled'}
    lTableFromCTP['0018-0010'] = {en = false, op = 'empty',   name = 'ContrastBolusAgent',                           comment = ''}
    lTableFromCTP['0018-0012'] = {en = false, op = '',        name = 'ContrastBolusAgentSeq',                        comment = ''}
    lTableFromCTP['0018-0014'] = {en = false, op = '',        name = 'ContrastBolusAdministrationRouteSeq',          comment = ''}
    lTableFromCTP['0018-0020'] = {en = false, op = '',        name = 'ScanningSeq',                                  comment = ''}
    lTableFromCTP['0018-0021'] = {en = false, op = '',        name = 'SeqVariant',                                   comment = ''}
    lTableFromCTP['0018-0022'] = {en = false, op = '',        name = 'ScanOptions',                                  comment = ''}
    lTableFromCTP['0018-0023'] = {en = false, op = '',        name = 'MRAcquisitionType',                            comment = ''}
    lTableFromCTP['0018-0024'] = {en = false, op = '',        name = 'SequenceName',                                 comment = ''}
    lTableFromCTP['0018-0025'] = {en = false, op = '',        name = 'AngioFlag',                                    comment = ''}
    lTableFromCTP['0018-0026'] = {en = false, op = '',        name = 'InterventionDrugInformationSeq',               comment = ''}
    lTableFromCTP['0018-0027'] = {en = false, op = '',        name = 'InterventionDrugStopTime',                     comment = ''}
    lTableFromCTP['0018-0028'] = {en = false, op = '',        name = 'InterventionDrugDose',                         comment = ''}
    lTableFromCTP['0018-0029'] = {en = false, op = '',        name = 'InterventionDrugCodeSeq',                      comment = ''}
    lTableFromCTP['0018-002a'] = {en = false, op = '',        name = 'AdditionalDrugSeq',                            comment = ''}
    lTableFromCTP['0018-0031'] = {en = false, op = '',        name = 'Radiopharmaceutical',                          comment = ''}
    lTableFromCTP['0018-0034'] = {en = false, op = '',        name = 'InterventionDrugName',                         comment = ''}
    lTableFromCTP['0018-0035'] = {en = false, op = '',        name = 'InterventionDrugStartTime',                    comment = ''}
    lTableFromCTP['0018-0036'] = {en = false, op = '',        name = 'InterventionalTherapySeq',                     comment = ''}
    lTableFromCTP['0018-0037'] = {en = false, op = '',        name = 'TherapyType',                                  comment = ''}
    lTableFromCTP['0018-0038'] = {en = false, op = '',        name = 'InterventionalStatus',                         comment = ''}
    lTableFromCTP['0018-0039'] = {en = false, op = '',        name = 'TherapyDescription',                           comment = ''}
    lTableFromCTP['0018-0040'] = {en = false, op = '',        name = 'CineRate',                                     comment = ''}
    lTableFromCTP['0018-0050'] = {en = false, op = '',        name = 'SliceThickness',                               comment = ''}
    lTableFromCTP['0018-0060'] = {en = false, op = '',        name = 'KVP',                                          comment = ''}
    lTableFromCTP['0018-0070'] = {en = false, op = '',        name = 'CountsAccumulated',                            comment = ''}
    lTableFromCTP['0018-0071'] = {en = false, op = '',        name = 'AcquisitionTerminationCondition',              comment = ''}
    lTableFromCTP['0018-0072'] = {en = false, op = '',        name = 'EffectiveSeriesDuration',                      comment = ''}
    lTableFromCTP['0018-0073'] = {en = false, op = '',        name = 'AcquisitionStartCondition',                    comment = ''}
    lTableFromCTP['0018-0074'] = {en = false, op = '',        name = 'AcquisitionStartConditionData',                comment = ''}
    lTableFromCTP['0018-0075'] = {en = false, op = '',        name = 'AcquisitionTerminationConditionData',          comment = ''}
    lTableFromCTP['0018-0080'] = {en = false, op = '',        name = 'RepetitionTime',                               comment = ''}
    lTableFromCTP['0018-0081'] = {en = true,  op = 'keep',    name = 'EchoTime',                                     comment = ''}
    lTableFromCTP['0018-0082'] = {en = false, op = '',        name = 'InversionTime',                                comment = ''}
    lTableFromCTP['0018-0083'] = {en = false, op = '',        name = 'NumberOfAverages',                             comment = ''}
    lTableFromCTP['0018-0084'] = {en = false, op = '',        name = 'ImagingFrequency',                             comment = ''}
    lTableFromCTP['0018-0085'] = {en = false, op = '',        name = 'ImagedNucleus',                                comment = ''}
    lTableFromCTP['0018-0086'] = {en = true,  op = 'keep',    name = 'EchoNumber',                                   comment = ''}
    lTableFromCTP['0018-0087'] = {en = false, op = '',        name = 'MagneticFieldStrength',                        comment = ''}
    lTableFromCTP['0018-0088'] = {en = false, op = '',        name = 'SpacingBetweenSlices',                         comment = ''}
    lTableFromCTP['0018-0089'] = {en = false, op = '',        name = 'NumberOfPhaseEncodingSteps',                   comment = ''}
    lTableFromCTP['0018-0090'] = {en = false, op = '',        name = 'DataCollectionDiameter',                       comment = ''}
    lTableFromCTP['0018-0091'] = {en = true,  op = 'keep',    name = 'EchoTrainLength',                              comment = ''}
    lTableFromCTP['0018-0093'] = {en = false, op = '',        name = 'PercentSampling',                              comment = ''}
    lTableFromCTP['0018-0094'] = {en = false, op = '',        name = 'PercentPhaseFieldOfView',                      comment = ''}
    lTableFromCTP['0018-0095'] = {en = false, op = '',        name = 'PixelBandwidth',                               comment = ''}
    lTableFromCTP['0018-1000'] = {en = true,  op = 'emptyx',  name = 'DeviceSerialNumber',                           comment = 'Per Clunie validator'}
    lTableFromCTP['0018-1002'] = {en = true,  op = 'remove',  name = 'DeviceUID',                                    comment = ''}
    lTableFromCTP['0018-1004'] = {en = true,  op = 'remove',  name = 'PlateID',                                      comment = ''}
    lTableFromCTP['0018-1005'] = {en = true,  op = 'remove',  name = 'GeneratorID',                                  comment = ''}
    lTableFromCTP['0018-1007'] = {en = true,  op = 'remove',  name = 'CassetteID',                                   comment = ''}
    lTableFromCTP['0018-1008'] = {en = true,  op = 'remove',  name = 'GantryID',                                     comment = ''}
    lTableFromCTP['0018-1010'] = {en = false, op = '',        name = 'SecondaryCaptureDeviceID',                     comment = ''}
    lTableFromCTP['0018-1011'] = {en = false, op = '',        name = 'HardcopyCreationDeviceID',                     comment = ''}
    lTableFromCTP['0018-1012'] = {en = true,  op = 'remove',  name = 'DateOfSecondaryCapture',                       comment = ''}
    lTableFromCTP['0018-1014'] = {en = false, op = '',        name = 'TimeOfSecondaryCapture',                       comment = ''}
    lTableFromCTP['0018-1016'] = {en = false, op = '',        name = 'SecondaryCaptureDeviceManufacturer',           comment = ''}
    lTableFromCTP['0018-1017'] = {en = false, op = '',        name = 'HardcopyDeviceManufacturer',                   comment = ''}
    lTableFromCTP['0018-1018'] = {en = false, op = '',        name = 'SecondaryCaptureDeviceManufacturerModelName',  comment = ''}
    lTableFromCTP['0018-1019'] = {en = false, op = '',        name = 'SecondaryCaptureDeviceSoftwareVersion',        comment = ''}
    lTableFromCTP['0018-101a'] = {en = false, op = '',        name = 'HardcopyDeviceSoftwareVersion',                comment = ''}
    lTableFromCTP['0018-101b'] = {en = false, op = '',        name = 'HardcopyDeviceManfuacturerModelName',          comment = ''}
    lTableFromCTP['0018-1020'] = {en = true,  op = 'emptyx',  name = 'SoftwareVersion',                              comment = 'Per Clunie validator'}
    lTableFromCTP['0018-1022'] = {en = false, op = '',        name = 'VideoImageFormatAcquired',                     comment = ''}
    lTableFromCTP['0018-1023'] = {en = false, op = '',        name = 'DigitalImageFormatAcquired',                   comment = ''}
    lTableFromCTP['0018-1030'] = {en = true,  op = 'keep',    name = 'ProtocolName',                                 comment = 'We often keeps this'}
    lTableFromCTP['0018-1040'] = {en = false, op = '',        name = 'ContrastBolusRoute',                           comment = ''}
    lTableFromCTP['0018-1041'] = {en = false, op = '',        name = 'ContrastBolusVolume',                          comment = ''}
    lTableFromCTP['0018-1042'] = {en = false, op = '',        name = 'ContrastBolusStartTime',                       comment = ''}
    lTableFromCTP['0018-1043'] = {en = false, op = '',        name = 'ContrastBolusStopTime',                        comment = ''}
    lTableFromCTP['0018-1044'] = {en = false, op = '',        name = 'ContrastBolusTotalDose',                       comment = ''}
    lTableFromCTP['0018-1045'] = {en = false, op = '',        name = 'SyringeCounts',                                comment = ''}
    lTableFromCTP['0018-1046'] = {en = false, op = '',        name = 'ContrastFlowRate',                             comment = ''}
    lTableFromCTP['0018-1047'] = {en = false, op = '',        name = 'ContrastFlowDuration',                         comment = ''}
    lTableFromCTP['0018-1048'] = {en = false, op = '',        name = 'ContrastBolusIngredient',                      comment = ''}
    lTableFromCTP['0018-1049'] = {en = false, op = '',        name = 'ContrastBolusIngredientConcentration',         comment = ''}
    lTableFromCTP['0018-1050'] = {en = false, op = '',        name = 'SpatialResolution',                            comment = ''}
    lTableFromCTP['0018-1060'] = {en = false, op = '',        name = 'TriggerTime',                                  comment = ''}
    lTableFromCTP['0018-1061'] = {en = false, op = '',        name = 'TriggerSourceOrType',                          comment = ''}
    lTableFromCTP['0018-1062'] = {en = false, op = '',        name = 'NominalInterval',                              comment = ''}
    lTableFromCTP['0018-1063'] = {en = false, op = '',        name = 'FrameTime',                                    comment = ''}
    lTableFromCTP['0018-1064'] = {en = false, op = '',        name = 'FramingType',                                  comment = ''}
    lTableFromCTP['0018-1065'] = {en = false, op = '',        name = 'FrameTimeVector',                              comment = ''}
    lTableFromCTP['0018-1066'] = {en = false, op = '',        name = 'FrameDelay',                                   comment = ''}
    lTableFromCTP['0018-1067'] = {en = false, op = '',        name = 'ImageTriggerDelay',                            comment = ''}
    lTableFromCTP['0018-1068'] = {en = false, op = '',        name = 'MultiplexGroupTimeOffset',                     comment = ''}
    lTableFromCTP['0018-1069'] = {en = false, op = '',        name = 'TriggerTimeOffset',                            comment = ''}
    lTableFromCTP['0018-106a'] = {en = false, op = '',        name = 'SynchronizationTrigger',                       comment = ''}
    lTableFromCTP['0018-106c'] = {en = false, op = '',        name = 'SynchronizationChannel',                       comment = ''}
    lTableFromCTP['0018-106e'] = {en = false, op = '',        name = 'TriggerSamplePosition',                        comment = ''}
    lTableFromCTP['0018-1070'] = {en = false, op = '',        name = 'RadiopharmaceuticalRoute',                     comment = ''}
    lTableFromCTP['0018-1071'] = {en = false, op = '',        name = 'RadiopharmaceuticalVolume',                    comment = ''}
    lTableFromCTP['0018-1072'] = {en = false, op = '',        name = 'RadiopharmaceuticalStartTime',                 comment = ''}
    lTableFromCTP['0018-1073'] = {en = false, op = '',        name = 'RadiopharmaceuticalStopTime',                  comment = ''}
    lTableFromCTP['0018-1074'] = {en = false, op = '',        name = 'RadionuclideTotalDose',                        comment = ''}
    lTableFromCTP['0018-1075'] = {en = false, op = '',        name = 'RadionuclideHalfLife',                         comment = ''}
    lTableFromCTP['0018-1076'] = {en = false, op = '',        name = 'RadionuclidePositronFraction',                 comment = ''}
    lTableFromCTP['0018-1077'] = {en = false, op = '',        name = 'RadiopharmaceuticalSpecificActivity',          comment = ''}
    lTableFromCTP['0018-1078'] = {en = true,  op = 'keep',    name = 'RadiopharmaceuticalStartDateTime',             comment = ''}
    lTableFromCTP['0018-1079'] = {en = true,  op = 'keep',    name = 'RadiopharmaceuticalStopDateTime',              comment = ''}
    lTableFromCTP['0018-1080'] = {en = false, op = '',        name = 'BeatRejectionFlag',                            comment = ''}
    lTableFromCTP['0018-1081'] = {en = false, op = '',        name = 'LowRRValue',                                   comment = ''}
    lTableFromCTP['0018-1082'] = {en = false, op = '',        name = 'HighRRValue',                                  comment = ''}
    lTableFromCTP['0018-1083'] = {en = false, op = '',        name = 'IntervalsAcquired',                            comment = ''}
    lTableFromCTP['0018-1084'] = {en = false, op = '',        name = 'IntervalsRejected',                            comment = ''}
    lTableFromCTP['0018-1085'] = {en = false, op = '',        name = 'PVCRejection',                                 comment = ''}
    lTableFromCTP['0018-1086'] = {en = false, op = '',        name = 'SkipBeats',                                    comment = ''}
    lTableFromCTP['0018-1088'] = {en = false, op = '',        name = 'HeartRate',                                    comment = ''}
    lTableFromCTP['0018-1090'] = {en = false, op = '',        name = 'CardiacNumberOfImages',                        comment = ''}
    lTableFromCTP['0018-1094'] = {en = false, op = '',        name = 'TriggerWindow',                                comment = ''}
    lTableFromCTP['0018-1100'] = {en = false, op = '',        name = 'ReconstructionDiameter',                       comment = ''}
    lTableFromCTP['0018-1110'] = {en = false, op = '',        name = 'DistanceSourceToDetector',                     comment = ''}
    lTableFromCTP['0018-1111'] = {en = false, op = '',        name = 'DistanceSourceToPatient',                      comment = ''}
    lTableFromCTP['0018-1114'] = {en = false, op = '',        name = 'EstimatedRadiographicMagnificationFactor',     comment = ''}
    lTableFromCTP['0018-1120'] = {en = false, op = '',        name = 'GantryDetectorTilt',                           comment = ''}
    lTableFromCTP['0018-1121'] = {en = false, op = '',        name = 'GantryDetectorSlew',                           comment = ''}
    lTableFromCTP['0018-1130'] = {en = false, op = '',        name = 'TableHeight',                                  comment = ''}
    lTableFromCTP['0018-1131'] = {en = false, op = '',        name = 'TableTraverse',                                comment = ''}
    lTableFromCTP['0018-1134'] = {en = false, op = '',        name = 'TableMotion',                                  comment = ''}
    lTableFromCTP['0018-1135'] = {en = false, op = '',        name = 'TableVerticalIncrement',                       comment = ''}
    lTableFromCTP['0018-1136'] = {en = false, op = '',        name = 'TableLateralIncrement',                        comment = ''}
    lTableFromCTP['0018-1137'] = {en = false, op = '',        name = 'TableLongitudinalIncrement',                   comment = ''}
    lTableFromCTP['0018-1138'] = {en = false, op = '',        name = 'TableAngle',                                   comment = ''}
    lTableFromCTP['0018-113a'] = {en = false, op = '',        name = 'TableType',                                    comment = ''}
    lTableFromCTP['0018-1140'] = {en = false, op = '',        name = 'RotationDirection',                            comment = ''}
    lTableFromCTP['0018-1141'] = {en = false, op = '',        name = 'AngularPosition',                              comment = ''}
    lTableFromCTP['0018-1142'] = {en = false, op = '',        name = 'RadialPosition',                               comment = ''}
    lTableFromCTP['0018-1143'] = {en = false, op = '',        name = 'ScanArc',                                      comment = ''}
    lTableFromCTP['0018-1144'] = {en = false, op = '',        name = 'AngularStep',                                  comment = ''}
    lTableFromCTP['0018-1145'] = {en = false, op = '',        name = 'CenterOfRotationOffset',                       comment = ''}
    lTableFromCTP['0018-1147'] = {en = false, op = '',        name = 'FieldOfViewShape',                             comment = ''}
    lTableFromCTP['0018-1149'] = {en = false, op = '',        name = 'FieldOfViewDimension',                         comment = ''}
    lTableFromCTP['0018-1150'] = {en = false, op = '',        name = 'ExposureTime',                                 comment = ''}
    lTableFromCTP['0018-1151'] = {en = false, op = '',        name = 'XRayTubeCurrent',                              comment = ''}
    lTableFromCTP['0018-1152'] = {en = false, op = '',        name = 'Exposure',                                     comment = ''}
    lTableFromCTP['0018-1153'] = {en = false, op = '',        name = 'ExposureInuAs',                                comment = ''}
    lTableFromCTP['0018-1154'] = {en = false, op = '',        name = 'AveragePulseWidth',                            comment = ''}
    lTableFromCTP['0018-1155'] = {en = false, op = '',        name = 'RadiationSetting',                             comment = ''}
    lTableFromCTP['0018-1156'] = {en = false, op = '',        name = 'RectificationType',                            comment = ''}
    lTableFromCTP['0018-115a'] = {en = false, op = '',        name = 'RadiationMode',                                comment = ''}
    lTableFromCTP['0018-115e'] = {en = false, op = '',        name = 'ImageAreaDoseProduct',                         comment = ''}
    lTableFromCTP['0018-1160'] = {en = false, op = '',        name = 'FilterType',                                   comment = ''}
    lTableFromCTP['0018-1161'] = {en = false, op = '',        name = 'TypeOfFilters',                                comment = ''}
    lTableFromCTP['0018-1162'] = {en = false, op = '',        name = 'IntensifierSize',                              comment = ''}
    lTableFromCTP['0018-1164'] = {en = false, op = '',        name = 'ImagerPixelSpacing',                           comment = ''}
    lTableFromCTP['0018-1166'] = {en = false, op = '',        name = 'Grid',                                         comment = ''}
    lTableFromCTP['0018-1170'] = {en = false, op = '',        name = 'GeneratorPower',                               comment = ''}
    lTableFromCTP['0018-1180'] = {en = false, op = '',        name = 'CollimatorGridName',                           comment = ''}
    lTableFromCTP['0018-1181'] = {en = false, op = '',        name = 'CollimatorType',                               comment = ''}
    lTableFromCTP['0018-1182'] = {en = false, op = '',        name = 'FocalDistance',                                comment = ''}
    lTableFromCTP['0018-1183'] = {en = false, op = '',        name = 'XFocusCenter',                                 comment = ''}
    lTableFromCTP['0018-1184'] = {en = false, op = '',        name = 'YFocusCenter',                                 comment = ''}
    lTableFromCTP['0018-1190'] = {en = false, op = '',        name = 'FocalSpot',                                    comment = ''}
    lTableFromCTP['0018-1191'] = {en = false, op = '',        name = 'AnodeTargetMaterial',                          comment = ''}
    lTableFromCTP['0018-11a0'] = {en = false, op = '',        name = 'BodyPartThickness',                            comment = ''}
    lTableFromCTP['0018-11a2'] = {en = false, op = '',        name = 'CompressionForce',                             comment = ''}
    lTableFromCTP['0018-1200'] = {en = true,  op = 'remove',  name = 'DateOfLastCalibration',                        comment = ''}
    lTableFromCTP['0018-1201'] = {en = false, op = '',        name = 'TimeOfLastCalibration',                        comment = ''}
    lTableFromCTP['0018-1210'] = {en = false, op = '',        name = 'ConvolutionKernel',                            comment = ''}
    lTableFromCTP['0018-1242'] = {en = false, op = '',        name = 'ActualFrameDuration',                          comment = ''}
    lTableFromCTP['0018-1243'] = {en = false, op = '',        name = 'CountRate',                                    comment = ''}
    lTableFromCTP['0018-1244'] = {en = false, op = '',        name = 'PreferredPlaybackSequencing',                  comment = ''}
    lTableFromCTP['0018-1250'] = {en = false, op = '',        name = 'ReceiveCoilName',                              comment = ''}
    lTableFromCTP['0018-1251'] = {en = false, op = '',        name = 'TransmitCoilName',                             comment = ''}
    lTableFromCTP['0018-1260'] = {en = false, op = '',        name = 'PlateType',                                    comment = ''}
    lTableFromCTP['0018-1261'] = {en = false, op = '',        name = 'PhosphorType',                                 comment = ''}
    lTableFromCTP['0018-1300'] = {en = false, op = '',        name = 'ScanVelocity',                                 comment = ''}
    lTableFromCTP['0018-1301'] = {en = false, op = '',        name = 'WholeBodyTechnique',                           comment = ''}
    lTableFromCTP['0018-1302'] = {en = false, op = '',        name = 'ScanLength',                                   comment = ''}
    lTableFromCTP['0018-1310'] = {en = false, op = '',        name = 'AcquisitionMatrix',                            comment = ''}
    lTableFromCTP['0018-1312'] = {en = false, op = '',        name = 'PhaseEncodingDirection',                       comment = ''}
    lTableFromCTP['0018-1314'] = {en = false, op = '',        name = 'FlipAngle',                                    comment = ''}
    lTableFromCTP['0018-1315'] = {en = false, op = '',        name = 'VariableFlipAngleFlag',                        comment = ''}
    lTableFromCTP['0018-1316'] = {en = false, op = '',        name = 'SAR',                                          comment = ''}
    lTableFromCTP['0018-1318'] = {en = false, op = '',        name = 'dBDt',                                         comment = ''}
    lTableFromCTP['0018-1400'] = {en = true,  op = 'remove',  name = 'AcquisitionDeviceProcessingDescription',       comment = ''}
    lTableFromCTP['0018-1401'] = {en = false, op = '',        name = 'AcquisitionDeviceProcessingCode',              comment = ''}
    lTableFromCTP['0018-1402'] = {en = false, op = '',        name = 'CassetteOrientation',                          comment = ''}
    lTableFromCTP['0018-1403'] = {en = false, op = '',        name = 'CassetteSize',                                 comment = ''}
    lTableFromCTP['0018-1404'] = {en = false, op = '',        name = 'ExposuresOnPlate',                             comment = ''}
    lTableFromCTP['0018-1405'] = {en = false, op = '',        name = 'RelativeXRayExposure',                         comment = ''}
    lTableFromCTP['0018-1450'] = {en = false, op = '',        name = 'ColumnAngulation',                             comment = ''}
    lTableFromCTP['0018-1460'] = {en = false, op = '',        name = 'TomoLayerHeight',                              comment = ''}
    lTableFromCTP['0018-1470'] = {en = false, op = '',        name = 'TomoAngle',                                    comment = ''}
    lTableFromCTP['0018-1480'] = {en = false, op = '',        name = 'TomoTime',                                     comment = ''}
    lTableFromCTP['0018-1490'] = {en = false, op = '',        name = 'TomoType',                                     comment = ''}
    lTableFromCTP['0018-1491'] = {en = false, op = '',        name = 'TomoClass',                                    comment = ''}
    lTableFromCTP['0018-1495'] = {en = false, op = '',        name = 'NumberofTomosynthesisSourceImages',            comment = ''}
    lTableFromCTP['0018-1500'] = {en = false, op = '',        name = 'PositionerMotion',                             comment = ''}
    lTableFromCTP['0018-1508'] = {en = false, op = '',        name = 'PositionerType',                               comment = ''}
    lTableFromCTP['0018-1510'] = {en = false, op = '',        name = 'PositionerPrimaryAngle',                       comment = ''}
    lTableFromCTP['0018-1511'] = {en = false, op = '',        name = 'PositionerSecondaryAngle',                     comment = ''}
    lTableFromCTP['0018-1520'] = {en = false, op = '',        name = 'PositionerPrimaryAngleIncrement',              comment = ''}
    lTableFromCTP['0018-1521'] = {en = false, op = '',        name = 'PositionerSecondaryAngleIncrement',            comment = ''}
    lTableFromCTP['0018-1530'] = {en = false, op = '',        name = 'DetectorPrimaryAngle',                         comment = ''}
    lTableFromCTP['0018-1531'] = {en = false, op = '',        name = 'DetectorSecondaryAngle',                       comment = ''}
    lTableFromCTP['0018-1600'] = {en = false, op = '',        name = 'ShutterShape',                                 comment = ''}
    lTableFromCTP['0018-1602'] = {en = false, op = '',        name = 'ShutterLeftVerticalEdge',                      comment = ''}
    lTableFromCTP['0018-1604'] = {en = false, op = '',        name = 'ShutterRightVerticalEdge',                     comment = ''}
    lTableFromCTP['0018-1606'] = {en = false, op = '',        name = 'ShutterUpperHorizontalEdge',                   comment = ''}
    lTableFromCTP['0018-1608'] = {en = false, op = '',        name = 'ShutterLowerHorizontalEdge',                   comment = ''}
    lTableFromCTP['0018-1610'] = {en = false, op = '',        name = 'CenterOfCircularShutter',                      comment = ''}
    lTableFromCTP['0018-1612'] = {en = false, op = '',        name = 'RadiusOfCircularShutter',                      comment = ''}
    lTableFromCTP['0018-1620'] = {en = false, op = '',        name = 'VerticesOfPolygonalShutter',                   comment = ''}
    lTableFromCTP['0018-1622'] = {en = false, op = '',        name = 'ShutterPresentationValue',                     comment = ''}
    lTableFromCTP['0018-1623'] = {en = false, op = '',        name = 'ShutterOverlayGroup',                          comment = ''}
    lTableFromCTP['0018-1700'] = {en = false, op = '',        name = 'CollimatorShape',                              comment = ''}
    lTableFromCTP['0018-1702'] = {en = false, op = '',        name = 'CollimatorLeftVerticalEdge',                   comment = ''}
    lTableFromCTP['0018-1704'] = {en = false, op = '',        name = 'CollimatorRightVerticalEdge',                  comment = ''}
    lTableFromCTP['0018-1706'] = {en = false, op = '',        name = 'CollimatorUpperHorizontalEdge',                comment = ''}
    lTableFromCTP['0018-1708'] = {en = false, op = '',        name = 'CollimatorLowerHorizontalEdge',                comment = ''}
    lTableFromCTP['0018-1710'] = {en = false, op = '',        name = 'CenterOfCircularCollimator',                   comment = ''}
    lTableFromCTP['0018-1712'] = {en = false, op = '',        name = 'RadiusOfCircularCollimator',                   comment = ''}
    lTableFromCTP['0018-1720'] = {en = false, op = '',        name = 'VerticesOfPolygonalCollimator',                comment = ''}
    lTableFromCTP['0018-1800'] = {en = false, op = '',        name = 'AcquisitionTimeSynchronized',                  comment = ''}
    lTableFromCTP['0018-1801'] = {en = false, op = '',        name = 'TimeSource',                                   comment = ''}
    lTableFromCTP['0018-1802'] = {en = false, op = '',        name = 'TimeDistributionProtocol',                     comment = ''}
    lTableFromCTP['0018-4000'] = {en = true,  op = 'remove',  name = 'AcquisitionComments',                          comment = ''}
    lTableFromCTP['0018-5000'] = {en = false, op = '',        name = 'OutputPower',                                  comment = ''}
    lTableFromCTP['0018-5010'] = {en = false, op = '',        name = 'TransducerData',                               comment = ''}
    lTableFromCTP['0018-5012'] = {en = false, op = '',        name = 'FocusDepth',                                   comment = ''}
    lTableFromCTP['0018-5020'] = {en = false, op = '',        name = 'ProcessingFunction',                           comment = ''}
    lTableFromCTP['0018-5021'] = {en = false, op = '',        name = 'PostprocessingFunction',                       comment = ''}
    lTableFromCTP['0018-5022'] = {en = false, op = '',        name = 'MechanicalIndex',                              comment = ''}
    lTableFromCTP['0018-5024'] = {en = false, op = '',        name = 'ThermalIndex',                                 comment = ''}
    lTableFromCTP['0018-5026'] = {en = false, op = '',        name = 'CranialThermalIndex',                          comment = ''}
    lTableFromCTP['0018-5027'] = {en = false, op = '',        name = 'SoftTissueThermalIndex',                       comment = ''}
    lTableFromCTP['0018-5028'] = {en = false, op = '',        name = 'SoftTissueFocusThermalIndex',                  comment = ''}
    lTableFromCTP['0018-5029'] = {en = false, op = '',        name = 'SoftTissueSurfaceThermalIndex',                comment = ''}
    lTableFromCTP['0018-5050'] = {en = false, op = '',        name = 'DepthOfScanField',                             comment = ''}
    lTableFromCTP['0018-5100'] = {en = false, op = '',        name = 'PatientPosition',                              comment = ''}
    lTableFromCTP['0018-5101'] = {en = false, op = '',        name = 'ViewPosition',                                 comment = ''}
    lTableFromCTP['0018-5104'] = {en = false, op = '',        name = 'ProjectionEponymousNameCodeSeq',               comment = ''}
    lTableFromCTP['0018-5210'] = {en = false, op = '',        name = 'ImageTransformationMatrix',                    comment = ''}
    lTableFromCTP['0018-5212'] = {en = false, op = '',        name = 'ImageTranslationVector',                       comment = ''}
    lTableFromCTP['0018-6000'] = {en = false, op = '',        name = 'Sensitivity',                                  comment = ''}
    lTableFromCTP['0018-6011'] = {en = false, op = '',        name = 'SeqOfUltrasoundRegions',                       comment = ''}
    lTableFromCTP['0018-6012'] = {en = false, op = '',        name = 'RegionSpatialFormat',                          comment = ''}
    lTableFromCTP['0018-6014'] = {en = false, op = '',        name = 'RegionDataType',                               comment = ''}
    lTableFromCTP['0018-6016'] = {en = false, op = '',        name = 'RegionFlags',                                  comment = ''}
    lTableFromCTP['0018-6018'] = {en = false, op = '',        name = 'RegionLocationMinX0',                          comment = ''}
    lTableFromCTP['0018-601a'] = {en = false, op = '',        name = 'RegionLocationMinY0',                          comment = ''}
    lTableFromCTP['0018-601c'] = {en = false, op = '',        name = 'RegionLocationMaxX1',                          comment = ''}
    lTableFromCTP['0018-601e'] = {en = false, op = '',        name = 'RegionLocationMaxY1',                          comment = ''}
    lTableFromCTP['0018-6020'] = {en = false, op = '',        name = 'ReferencePixelX0',                             comment = ''}
    lTableFromCTP['0018-6022'] = {en = false, op = '',        name = 'ReferencePixelY0',                             comment = ''}
    lTableFromCTP['0018-6024'] = {en = false, op = '',        name = 'PhysicalUnitsXDirection',                      comment = ''}
    lTableFromCTP['0018-6026'] = {en = false, op = '',        name = 'PhysicalUnitsYDirection',                      comment = ''}
    lTableFromCTP['0018-6028'] = {en = false, op = '',        name = 'ReferencePixelPhysicalValueX',                 comment = ''}
    lTableFromCTP['0018-602a'] = {en = false, op = '',        name = 'ReferencePixelPhysicalValueY',                 comment = ''}
    lTableFromCTP['0018-602c'] = {en = false, op = '',        name = 'PhysicalDeltaX',                               comment = ''}
    lTableFromCTP['0018-602e'] = {en = false, op = '',        name = 'PhysicalDeltaY',                               comment = ''}
    lTableFromCTP['0018-6030'] = {en = false, op = '',        name = 'TransducerFrequency',                          comment = ''}
    lTableFromCTP['0018-6031'] = {en = false, op = '',        name = 'TransducerType',                               comment = ''}
    lTableFromCTP['0018-6032'] = {en = false, op = '',        name = 'PulseRepetitionFrequency',                     comment = ''}
    lTableFromCTP['0018-6034'] = {en = false, op = '',        name = 'DopplerCorrectionAngle',                       comment = ''}
    lTableFromCTP['0018-6036'] = {en = false, op = '',        name = 'SteeringAngle',                                comment = ''}
    lTableFromCTP['0018-6038'] = {en = false, op = '',        name = 'DopplerSampleVolumeXPosition',                 comment = ''}
    lTableFromCTP['0018-603a'] = {en = false, op = '',        name = 'DopplerSampleVolumeYPosition',                 comment = ''}
    lTableFromCTP['0018-603c'] = {en = false, op = '',        name = 'TMLinePositionX0',                             comment = ''}
    lTableFromCTP['0018-603e'] = {en = false, op = '',        name = 'TMLinePositionY0',                             comment = ''}
    lTableFromCTP['0018-6040'] = {en = false, op = '',        name = 'TMLinePositionX1',                             comment = ''}
    lTableFromCTP['0018-6042'] = {en = false, op = '',        name = 'TMLinePositionY1',                             comment = ''}
    lTableFromCTP['0018-6044'] = {en = false, op = '',        name = 'PixelComponentOrganization',                   comment = ''}
    lTableFromCTP['0018-6046'] = {en = false, op = '',        name = 'PixelComponentMask',                           comment = ''}
    lTableFromCTP['0018-6048'] = {en = false, op = '',        name = 'PixelComponentRangeStart',                     comment = ''}
    lTableFromCTP['0018-604a'] = {en = false, op = '',        name = 'PixelComponentRangeStop',                      comment = ''}
    lTableFromCTP['0018-604c'] = {en = false, op = '',        name = 'PixelComponentPhysicalUnits',                  comment = ''}
    lTableFromCTP['0018-604e'] = {en = false, op = '',        name = 'PixelComponentDataType',                       comment = ''}
    lTableFromCTP['0018-6050'] = {en = false, op = '',        name = 'NumberOfTableBreakPoints',                     comment = ''}
    lTableFromCTP['0018-6052'] = {en = false, op = '',        name = 'TableOfXBreakPoints',                          comment = ''}
    lTableFromCTP['0018-6054'] = {en = false, op = '',        name = 'TableOfYBreakPoints',                          comment = ''}
    lTableFromCTP['0018-6056'] = {en = false, op = '',        name = 'NumberOfTableEntries',                         comment = ''}
    lTableFromCTP['0018-6058'] = {en = false, op = '',        name = 'TableOfPixelValues',                           comment = ''}
    lTableFromCTP['0018-605a'] = {en = false, op = '',        name = 'TableOfParameterValues',                       comment = ''}
    lTableFromCTP['0018-7000'] = {en = false, op = '',        name = 'DetectorConditionsNominalFlag',                comment = ''}
    lTableFromCTP['0018-7001'] = {en = false, op = '',        name = 'DetectorTemperature',                          comment = ''}
    lTableFromCTP['0018-7004'] = {en = false, op = '',        name = 'DetectorType',                                 comment = ''}
    lTableFromCTP['0018-7005'] = {en = false, op = '',        name = 'DetectorConfiguration',                        comment = ''}
    lTableFromCTP['0018-7006'] = {en = false, op = '',        name = 'DetectorDescription',                          comment = ''}
    lTableFromCTP['0018-7008'] = {en = false, op = '',        name = 'DetectorMode',                                 comment = ''}
    lTableFromCTP['0018-700a'] = {en = true,  op = 'remove',  name = 'DetectorID',                                   comment = ''}
    lTableFromCTP['0018-700c'] = {en = true,  op = 'remove',  name = 'DateOfLastDetectorCalibration',                comment = ''}
    lTableFromCTP['0018-700e'] = {en = false, op = '',        name = 'TimeOfLastDetectorCalibration',                comment = ''}
    lTableFromCTP['0018-7010'] = {en = false, op = '',        name = 'ExposuresOnDetectorSinceLastCalibration',      comment = ''}
    lTableFromCTP['0018-7011'] = {en = false, op = '',        name = 'ExposuresOnDetectorSinceManufactured',         comment = ''}
    lTableFromCTP['0018-7012'] = {en = false, op = '',        name = 'DetectorTimeSinceLastExposure',                comment = ''}
    lTableFromCTP['0018-7014'] = {en = false, op = '',        name = 'DetectorActiveTime',                           comment = ''}
    lTableFromCTP['0018-7016'] = {en = false, op = '',        name = 'DetectorActivationOffsetFromExposure',         comment = ''}
    lTableFromCTP['0018-701a'] = {en = false, op = '',        name = 'DetectorBinning',                              comment = ''}
    lTableFromCTP['0018-7020'] = {en = false, op = '',        name = 'DetectorElementPhysicalSize',                  comment = ''}
    lTableFromCTP['0018-7022'] = {en = false, op = '',        name = 'DetectorElementSpacing',                       comment = ''}
    lTableFromCTP['0018-7024'] = {en = false, op = '',        name = 'DetectorActiveShape',                          comment = ''}
    lTableFromCTP['0018-7026'] = {en = false, op = '',        name = 'DetectorActiveDimension',                      comment = ''}
    lTableFromCTP['0018-7028'] = {en = false, op = '',        name = 'DetectorActiveOrigin',                         comment = ''}
    lTableFromCTP['0018-7030'] = {en = false, op = '',        name = 'FieldOfViewOrigin',                            comment = ''}
    lTableFromCTP['0018-7032'] = {en = false, op = '',        name = 'FieldOfViewRotation',                          comment = ''}
    lTableFromCTP['0018-7034'] = {en = false, op = '',        name = 'FieldOfViewHorizontalFlip',                    comment = ''}
    lTableFromCTP['0018-7040'] = {en = false, op = '',        name = 'GridAbsorbingMaterial',                        comment = ''}
    lTableFromCTP['0018-7041'] = {en = false, op = '',        name = 'GridSpacingMaterial',                          comment = ''}
    lTableFromCTP['0018-7042'] = {en = false, op = '',        name = 'GridThickness',                                comment = ''}
    lTableFromCTP['0018-7044'] = {en = false, op = '',        name = 'GridPitch',                                    comment = ''}
    lTableFromCTP['0018-7046'] = {en = false, op = '',        name = 'GridAspectRatio',                              comment = ''}
    lTableFromCTP['0018-7048'] = {en = false, op = '',        name = 'GridPeriod',                                   comment = ''}
    lTableFromCTP['0018-704c'] = {en = false, op = '',        name = 'GridFocalDistance',                            comment = ''}
    lTableFromCTP['0018-7050'] = {en = false, op = '',        name = 'FilterMaterial',                               comment = ''}
    lTableFromCTP['0018-7052'] = {en = false, op = '',        name = 'FilterThicknessMinimum',                       comment = ''}
    lTableFromCTP['0018-7054'] = {en = false, op = '',        name = 'FilterThicknessMaximum',                       comment = ''}
    lTableFromCTP['0018-7060'] = {en = false, op = '',        name = 'ExposureControlMode',                          comment = ''}
    lTableFromCTP['0018-7062'] = {en = false, op = '',        name = 'ExposureControlModeDescription',               comment = ''}
    lTableFromCTP['0018-7064'] = {en = false, op = '',        name = 'ExposureStatus',                               comment = ''}
    lTableFromCTP['0018-7065'] = {en = false, op = '',        name = 'PhototimerSetting',                            comment = ''}
    lTableFromCTP['0018-8150'] = {en = false, op = '',        name = 'ExposureTimeInuS',                             comment = ''}
    lTableFromCTP['0018-8151'] = {en = false, op = '',        name = 'XRayTubeCurrentInuA',                          comment = ''}
    lTableFromCTP['0018-9004'] = {en = false, op = '',        name = 'ContentQualification',                         comment = ''}
    lTableFromCTP['0018-9005'] = {en = false, op = '',        name = 'PulseSequenceName',                            comment = ''}
    lTableFromCTP['0018-9006'] = {en = false, op = '',        name = 'MRImagingModifierSeq',                         comment = ''}
    lTableFromCTP['0018-9008'] = {en = false, op = '',        name = 'EchoPulseSeq',                                 comment = ''}
    lTableFromCTP['0018-9009'] = {en = false, op = '',        name = 'InversionRecovery',                            comment = ''}
    lTableFromCTP['0018-9010'] = {en = false, op = '',        name = 'FlowCompensation',                             comment = ''}
    lTableFromCTP['0018-9011'] = {en = false, op = '',        name = 'MultipleSpinEcho',                             comment = ''}
    lTableFromCTP['0018-9012'] = {en = false, op = '',        name = 'MultiPlanarExcitation',                        comment = ''}
    lTableFromCTP['0018-9014'] = {en = false, op = '',        name = 'PhaseContrast',                                comment = ''}
    lTableFromCTP['0018-9015'] = {en = false, op = '',        name = 'TimeOfFlightContrast',                         comment = ''}
    lTableFromCTP['0018-9016'] = {en = false, op = '',        name = 'Spoiling',                                     comment = ''}
    lTableFromCTP['0018-9017'] = {en = false, op = '',        name = 'SteadyStatePulseSeq',                          comment = ''}
    lTableFromCTP['0018-9018'] = {en = false, op = '',        name = 'EchoPlanarPulseSeq',                           comment = ''}
    lTableFromCTP['0018-9019'] = {en = false, op = '',        name = 'TagAngleFirstAxis',                            comment = ''}
    lTableFromCTP['0018-9020'] = {en = false, op = '',        name = 'MagnetizationTransfer',                        comment = ''}
    lTableFromCTP['0018-9021'] = {en = false, op = '',        name = 'T2Preparation',                                comment = ''}
    lTableFromCTP['0018-9022'] = {en = false, op = '',        name = 'BloodSignalNulling',                           comment = ''}
    lTableFromCTP['0018-9024'] = {en = false, op = '',        name = 'SaturationRecovery',                           comment = ''}
    lTableFromCTP['0018-9025'] = {en = false, op = '',        name = 'SpectrallySelectedSuppression',                comment = ''}
    lTableFromCTP['0018-9026'] = {en = false, op = '',        name = 'SpectrallySelectedExcitation',                 comment = ''}
    lTableFromCTP['0018-9027'] = {en = false, op = '',        name = 'SpatialPreSaturation',                         comment = ''}
    lTableFromCTP['0018-9028'] = {en = false, op = '',        name = 'Tagging',                                      comment = ''}
    lTableFromCTP['0018-9029'] = {en = false, op = '',        name = 'OversamplingPhase',                            comment = ''}
    lTableFromCTP['0018-9030'] = {en = false, op = '',        name = 'TagSpacingFirstDimension',                     comment = ''}
    lTableFromCTP['0018-9032'] = {en = false, op = '',        name = 'GeometryOfKSpaceTraversal',                    comment = ''}
    lTableFromCTP['0018-9033'] = {en = false, op = '',        name = 'SegmentedKSpaceTraversal',                     comment = ''}
    lTableFromCTP['0018-9034'] = {en = false, op = '',        name = 'RectilinearPhaseEncodeReordering',             comment = ''}
    lTableFromCTP['0018-9035'] = {en = false, op = '',        name = 'TagThickness',                                 comment = ''}
    lTableFromCTP['0018-9036'] = {en = false, op = '',        name = 'PartialFourierDirection',                      comment = ''}
    lTableFromCTP['0018-9037'] = {en = false, op = '',        name = 'GatingSynchronizationTechnique',               comment = ''}
    lTableFromCTP['0018-9041'] = {en = false, op = '',        name = 'ReceiveCoilManufacturerName',                  comment = ''}
    lTableFromCTP['0018-9042'] = {en = false, op = '',        name = 'MRReceiveCoilSeq',                             comment = ''}
    lTableFromCTP['0018-9043'] = {en = false, op = '',        name = 'ReceiveCoilType',                              comment = ''}
    lTableFromCTP['0018-9044'] = {en = false, op = '',        name = 'QuadratureReceiveCoil',                        comment = ''}
    lTableFromCTP['0018-9045'] = {en = false, op = '',        name = 'MultiCoilDefinitionSeq',                       comment = ''}
    lTableFromCTP['0018-9046'] = {en = false, op = '',        name = 'MultiCoilConfiguration',                       comment = ''}
    lTableFromCTP['0018-9047'] = {en = false, op = '',        name = 'MultiCoilElementName',                         comment = ''}
    lTableFromCTP['0018-9048'] = {en = false, op = '',        name = 'MultiCoilElementUsed',                         comment = ''}
    lTableFromCTP['0018-9049'] = {en = false, op = '',        name = 'MRTransmitCoilSeq',                            comment = ''}
    lTableFromCTP['0018-9050'] = {en = false, op = '',        name = 'TransmitCoilManufacturerName',                 comment = ''}
    lTableFromCTP['0018-9051'] = {en = false, op = '',        name = 'TransmitCoilType',                             comment = ''}
    lTableFromCTP['0018-9052'] = {en = false, op = '',        name = 'SpectralWidth',                                comment = ''}
    lTableFromCTP['0018-9053'] = {en = false, op = '',        name = 'ChemicalShiftReference',                       comment = ''}
    lTableFromCTP['0018-9054'] = {en = false, op = '',        name = 'VolumeLocalizationTechnique',                  comment = ''}
    lTableFromCTP['0018-9058'] = {en = false, op = '',        name = 'MRAcquisitionFrequencyEncodingSteps',          comment = ''}
    lTableFromCTP['0018-9059'] = {en = false, op = '',        name = 'DeCoupling',                                   comment = ''}
    lTableFromCTP['0018-9060'] = {en = false, op = '',        name = 'DeCoupledNucleus',                             comment = ''}
    lTableFromCTP['0018-9061'] = {en = false, op = '',        name = 'DeCouplingFrequency',                          comment = ''}
    lTableFromCTP['0018-9062'] = {en = false, op = '',        name = 'DeCouplingMethod',                             comment = ''}
    lTableFromCTP['0018-9063'] = {en = false, op = '',        name = 'DeCouplingChemicalShiftReference',             comment = ''}
    lTableFromCTP['0018-9064'] = {en = false, op = '',        name = 'KSpaceFiltering',                              comment = ''}
    lTableFromCTP['0018-9065'] = {en = false, op = '',        name = 'TimeDomainFiltering',                          comment = ''}
    lTableFromCTP['0018-9066'] = {en = false, op = '',        name = 'NumberOfZeroFills',                            comment = ''}
    lTableFromCTP['0018-9067'] = {en = false, op = '',        name = 'BaselineCorrection',                           comment = ''}
    lTableFromCTP['0018-9070'] = {en = false, op = '',        name = 'CardiacRRIntervalSpecified',                   comment = ''}
    lTableFromCTP['0018-9073'] = {en = false, op = '',        name = 'AcquisitionDuration',                          comment = ''}
    lTableFromCTP['0018-9074'] = {en = true,  op = 'keep',    name = 'FrameAcquisitionDatetime',                     comment = 'Per Clunie validator'}
    lTableFromCTP['0018-9075'] = {en = false, op = '',        name = 'DiffusionDirectionality',                      comment = ''}
    lTableFromCTP['0018-9076'] = {en = false, op = '',        name = 'DiffusionGradientDirectionSeq',                comment = ''}
    lTableFromCTP['0018-9077'] = {en = false, op = '',        name = 'ParallelAcquisition',                          comment = ''}
    lTableFromCTP['0018-9078'] = {en = false, op = '',        name = 'ParallelAcquisitionTechnique',                 comment = ''}
    lTableFromCTP['0018-9079'] = {en = false, op = '',        name = 'InversionTimes',                               comment = ''}
    lTableFromCTP['0018-9080'] = {en = false, op = '',        name = 'MetaboliteMapDescription',                     comment = ''}
    lTableFromCTP['0018-9081'] = {en = false, op = '',        name = 'PartialFourier',                               comment = ''}
    lTableFromCTP['0018-9082'] = {en = false, op = '',        name = 'EffectiveEchoTime',                            comment = ''}
    lTableFromCTP['0018-9084'] = {en = false, op = '',        name = 'ChemicalShiftSeq',                             comment = ''}
    lTableFromCTP['0018-9085'] = {en = false, op = '',        name = 'CardiacSignalSource',                          comment = ''}
    lTableFromCTP['0018-9087'] = {en = false, op = '',        name = 'DiffusionBValue',                              comment = ''}
    lTableFromCTP['0018-9089'] = {en = false, op = '',        name = 'DiffusionGradientOrientation',                 comment = ''}
    lTableFromCTP['0018-9090'] = {en = false, op = '',        name = 'VelocityEncodingDirection',                    comment = ''}
    lTableFromCTP['0018-9091'] = {en = false, op = '',        name = 'VelocityEncodingMinimumValue',                 comment = ''}
    lTableFromCTP['0018-9093'] = {en = false, op = '',        name = 'NumberOfKSpaceTrajectories',                   comment = ''}
    lTableFromCTP['0018-9094'] = {en = false, op = '',        name = 'CoverageOfKSpace',                             comment = ''}
    lTableFromCTP['0018-9095'] = {en = false, op = '',        name = 'SpectroscopyAcquisitionPhaseRows',             comment = ''}
    lTableFromCTP['0018-9096'] = {en = false, op = '',        name = 'ParallelReductionFactorInPlane',               comment = ''}
    lTableFromCTP['0018-9098'] = {en = false, op = '',        name = 'TransmitterFrequency',                         comment = ''}
    lTableFromCTP['0018-9100'] = {en = false, op = '',        name = 'ResonantNucleus',                              comment = ''}
    lTableFromCTP['0018-9101'] = {en = false, op = '',        name = 'FrequencyCorrection',                          comment = ''}
    lTableFromCTP['0018-9103'] = {en = false, op = '',        name = 'MRSpectroscopyFOVGeometrySeq',                 comment = ''}
    lTableFromCTP['0018-9104'] = {en = false, op = '',        name = 'SlabThickness',                                comment = ''}
    lTableFromCTP['0018-9105'] = {en = false, op = '',        name = 'SlabOrientation',                              comment = ''}
    lTableFromCTP['0018-9106'] = {en = false, op = '',        name = 'MidSlabPosition',                              comment = ''}
    lTableFromCTP['0018-9107'] = {en = false, op = '',        name = 'MRSpatialSaturationSeq',                       comment = ''}
    lTableFromCTP['0018-9112'] = {en = false, op = '',        name = 'MRTimingAndRelatedParametersSeq',              comment = ''}
    lTableFromCTP['0018-9114'] = {en = false, op = '',        name = 'MREchoSeq',                                    comment = ''}
    lTableFromCTP['0018-9115'] = {en = false, op = '',        name = 'MRModifierSeq',                                comment = ''}
    lTableFromCTP['0018-9117'] = {en = false, op = '',        name = 'MRDiffusionSeq',                               comment = ''}
    lTableFromCTP['0018-9118'] = {en = false, op = '',        name = 'CardiacTriggerSeq',                            comment = ''}
    lTableFromCTP['0018-9119'] = {en = false, op = '',        name = 'MRAveragesSeq',                                comment = ''}
    lTableFromCTP['0018-9125'] = {en = false, op = '',        name = 'MRFOVGeometrySeq',                             comment = ''}
    lTableFromCTP['0018-9126'] = {en = false, op = '',        name = 'VolumeLocalizationSeq',                        comment = ''}
    lTableFromCTP['0018-9127'] = {en = false, op = '',        name = 'SpectroscopyAcquisitionDataColumns',           comment = ''}
    lTableFromCTP['0018-9147'] = {en = false, op = '',        name = 'DiffusionAnisotropyType',                      comment = ''}
    lTableFromCTP['0018-9151'] = {en = true,  op = 'keep',    name = 'FrameReferenceDatetime',                       comment = 'Per Clunie validator'}
    lTableFromCTP['0018-9152'] = {en = false, op = '',        name = 'MetaboliteMapSeq',                             comment = ''}
    lTableFromCTP['0018-9155'] = {en = false, op = '',        name = 'ParallelReductionFactorOutOfPlane',            comment = ''}
    lTableFromCTP['0018-9159'] = {en = false, op = '',        name = 'SpectroscopyAcquisitionOutOfPlanePhaseSteps',  comment = ''}
    lTableFromCTP['0018-9166'] = {en = false, op = '',        name = 'BulkMotionStatus',                             comment = ''}
    lTableFromCTP['0018-9168'] = {en = true,  op = 'keep',    name = 'ParallelReductionFactorSecondInPlane',         comment = 'Per Clunie validator'}
    lTableFromCTP['0018-9169'] = {en = false, op = '',        name = 'CardiacBeatRejectionTechnique',                comment = ''}
    lTableFromCTP['0018-9170'] = {en = false, op = '',        name = 'RespiratoryMotionCompensation',                comment = ''}
    lTableFromCTP['0018-9171'] = {en = false, op = '',        name = 'RespiratorySignalSource',                      comment = ''}
    lTableFromCTP['0018-9172'] = {en = false, op = '',        name = 'BulkMotionCompensationTechnique',              comment = ''}
    lTableFromCTP['0018-9173'] = {en = false, op = '',        name = 'BulkMotionSignal',                             comment = ''}
    lTableFromCTP['0018-9174'] = {en = false, op = '',        name = 'ApplicableSafetyStandardAgency',               comment = ''}
    lTableFromCTP['0018-9175'] = {en = false, op = '',        name = 'ApplicableSafetyStandardVersion',              comment = ''}
    lTableFromCTP['0018-9176'] = {en = false, op = '',        name = 'OperationModeSeq',                             comment = ''}
    lTableFromCTP['0018-9177'] = {en = false, op = '',        name = 'OperatingModeType',                            comment = ''}
    lTableFromCTP['0018-9178'] = {en = false, op = '',        name = 'OperationMode',                                comment = ''}
    lTableFromCTP['0018-9179'] = {en = false, op = '',        name = 'SpecificAbsorptionRateDefinition',             comment = ''}
    lTableFromCTP['0018-9180'] = {en = false, op = '',        name = 'GradientOutputType',                           comment = ''}
    lTableFromCTP['0018-9181'] = {en = false, op = '',        name = 'SpecificAbsorptionRateValue',                  comment = ''}
    lTableFromCTP['0018-9182'] = {en = false, op = '',        name = 'GradientOutput',                               comment = ''}
    lTableFromCTP['0018-9183'] = {en = false, op = '',        name = 'FlowCompensationDirection',                    comment = ''}
    lTableFromCTP['0018-9184'] = {en = false, op = '',        name = 'TaggingDelay',                                 comment = ''}
    lTableFromCTP['0018-9195'] = {en = false, op = '',        name = 'ChemicalShiftsMinimumIntegrationLimit',        comment = ''}
    lTableFromCTP['0018-9196'] = {en = false, op = '',        name = 'ChemicalShiftsMaximumIntegrationLimit',        comment = ''}
    lTableFromCTP['0018-9197'] = {en = false, op = '',        name = 'MRVelocityEncodingSeq',                        comment = ''}
    lTableFromCTP['0018-9198'] = {en = false, op = '',        name = 'FirstOrderPhaseCorrection',                    comment = ''}
    lTableFromCTP['0018-9199'] = {en = false, op = '',        name = 'WaterReferencedPhaseCorrection',               comment = ''}
    lTableFromCTP['0018-9200'] = {en = false, op = '',        name = 'MRSpectroscopyAcquisitionType',                comment = ''}
    lTableFromCTP['0018-9214'] = {en = false, op = '',        name = 'RespiratoryMotionStatus',                      comment = ''}
    lTableFromCTP['0018-9217'] = {en = false, op = '',        name = 'VelocityEncodingMaximumValue',                 comment = ''}
    lTableFromCTP['0018-9218'] = {en = false, op = '',        name = 'TagSpacingSecondDimension',                    comment = ''}
    lTableFromCTP['0018-9219'] = {en = false, op = '',        name = 'TagAngleSecondAxis',                           comment = ''}
    lTableFromCTP['0018-9220'] = {en = false, op = '',        name = 'FrameAcquisitionDuration',                     comment = ''}
    lTableFromCTP['0018-9226'] = {en = false, op = '',        name = 'MRImageFrameTypeSeq',                          comment = ''}
    lTableFromCTP['0018-9227'] = {en = false, op = '',        name = 'MRSpectroscopyFrameTypeSeq',                   comment = ''}
    lTableFromCTP['0018-9231'] = {en = false, op = '',        name = 'MRAcquisitionPhaseEncodingStepsInPlane',       comment = ''}
    lTableFromCTP['0018-9232'] = {en = false, op = '',        name = 'MRAcquisitionPhaseEncodingStepsOutOfPlane',    comment = ''}
    lTableFromCTP['0018-9234'] = {en = false, op = '',        name = 'SpectroscopyAcquisitionPhaseColumns',          comment = ''}
    lTableFromCTP['0018-9236'] = {en = false, op = '',        name = 'CardiacMotionStatus',                          comment = ''}
    lTableFromCTP['0018-9239'] = {en = false, op = '',        name = 'SpecificAbsorptionRateSeq',                    comment = ''}
    lTableFromCTP['0018-9424'] = {en = true,  op = 'remove',  name = 'AcquisitionProtocolDescription',               comment = ''}
    lTableFromCTP['0018-a003'] = {en = true,  op = 'remove',  name = 'ContributionDescription',                      comment = ''}
    if lFlagHologic or lFlagKeepSiemensMR then
        lTableFromCTP['0019'] = { en = true,  op = 'groupkeep', name = 'SiemensMRHeader',                            comment = 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
    end
    lTableFromCTP['0020-000d'] = {en = true,  op = 'orthanc', name = 'StudyInstanceUID',                             comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0020-000e'] = {en = true,  op = 'orthanc', name = 'SeriesInstanceUID',                            comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0020-0010'] = {en = true,  op = 'keep',    name = 'StudyID',                                      comment = 'Orthanc later anonymizes this'}
    lTableFromCTP['0020-0011'] = {en = false, op = '',        name = 'SeriesNumber',                                 comment = ''}
    lTableFromCTP['0020-0012'] = {en = false, op = '',        name = 'AcquisitionNumber',                            comment = ''}
    lTableFromCTP['0020-0013'] = {en = false, op = '',        name = 'InstanceNumber',                               comment = ''}
    lTableFromCTP['0020-0019'] = {en = false, op = '',        name = 'ItemNumber',                                   comment = ''}
    lTableFromCTP['0020-0020'] = {en = false, op = '',        name = 'PatientOrientation',                           comment = ''}
    lTableFromCTP['0020-0022'] = {en = false, op = '',        name = 'OverlayNumber',                                comment = ''}
    lTableFromCTP['0020-0024'] = {en = false, op = '',        name = 'CurveNumber',                                  comment = ''}
    lTableFromCTP['0020-0026'] = {en = false, op = '',        name = 'LUTNumber',                                    comment = ''}
    lTableFromCTP['0020-0032'] = {en = false, op = '',        name = 'ImagePosition',                                comment = ''}
    lTableFromCTP['0020-0037'] = {en = false, op = '',        name = 'ImageOrientation',                             comment = ''}
    lTableFromCTP['0020-0052'] = {en = true,  op = 'orthanc', name = 'FrameOfReferenceUID',                          comment = 'Currently handled by Orthanc'}
    lTableFromCTP['0020-0060'] = {en = false, op = '',        name = 'Laterality',                                   comment = ''}
    lTableFromCTP['0020-0062'] = {en = false, op = '',        name = 'ImageLaterality',                              comment = ''}
    lTableFromCTP['0020-0100'] = {en = false, op = '',        name = 'TemporalPositionIdentifier',                   comment = ''}
    lTableFromCTP['0020-0105'] = {en = false, op = '',        name = 'NumberOfTemporalPositions',                    comment = ''}
    lTableFromCTP['0020-0110'] = {en = false, op = '',        name = 'TemporalResolution',                           comment = ''}
    lTableFromCTP['0020-0200'] = {en = true,  op = 'remove',  name = 'SynchronizationFrameOfReferenceUID',           comment = ''}
    lTableFromCTP['0020-1000'] = {en = false, op = '',        name = 'SeriesInStudy',                                comment = ''}
    lTableFromCTP['0020-1002'] = {en = false, op = '',        name = 'ImagesInAcquisition',                          comment = ''}
    lTableFromCTP['0020-1004'] = {en = false, op = '',        name = 'AcquisitionsInStudy',                          comment = ''}
    lTableFromCTP['0020-1040'] = {en = false, op = '',        name = 'PositionReferenceIndicator',                   comment = ''}
    lTableFromCTP['0020-1041'] = {en = false, op = '',        name = 'SliceLocation',                                comment = ''}
    lTableFromCTP['0020-1070'] = {en = false, op = '',        name = 'OtherStudyNumbers',                            comment = ''}
    lTableFromCTP['0020-1200'] = {en = false, op = '',        name = 'NumberOfPatientRelatedStudies',                comment = ''}
    lTableFromCTP['0020-1202'] = {en = false, op = '',        name = 'NumberOfPatientRelatedSeries',                 comment = ''}
    lTableFromCTP['0020-1204'] = {en = false, op = '',        name = 'NumberOfPatientRelatedInstances',              comment = ''}
    lTableFromCTP['0020-1206'] = {en = false, op = '',        name = 'NumberOfStudyRelatedSeries',                   comment = ''}
    lTableFromCTP['0020-1208'] = {en = false, op = '',        name = 'NumberOfStudyRelatedInstances',                comment = ''}
    lTableFromCTP['0020-1209'] = {en = false, op = '',        name = 'NumberOfSeriesRelatedInstances',               comment = ''}
    lTableFromCTP['0020-3401'] = {en = true,  op = 'remove',  name = 'ModifyingDeviceID',                            comment = ''}
    lTableFromCTP['0020-3404'] = {en = true,  op = 'remove',  name = 'ModifyingDeviceManufacturer',                  comment = ''}
    lTableFromCTP['0020-3406'] = {en = true,  op = 'remove',  name = 'ModifiedImageDescription',                     comment = ''}
    lTableFromCTP['0020-4000'] = {en = true,  op = 'remove',  name = 'ImageComments',                                comment = 'We often keeps this, but siemens retro-recon puts PHI here'}
    lTableFromCTP['0020-9056'] = {en = false, op = '',        name = 'StackID',                                      comment = ''}
    lTableFromCTP['0020-9057'] = {en = false, op = '',        name = 'InStackPositionNumber',                        comment = ''}
    lTableFromCTP['0020-9071'] = {en = false, op = '',        name = 'FrameAnatomySeq',                              comment = ''}
    lTableFromCTP['0020-9072'] = {en = false, op = '',        name = 'FrameLaterality',                              comment = ''}
    lTableFromCTP['0020-9111'] = {en = false, op = '',        name = 'FrameContentSeq',                              comment = ''}
    lTableFromCTP['0020-9113'] = {en = false, op = '',        name = 'PlanePositionSeq',                             comment = ''}
    lTableFromCTP['0020-9116'] = {en = false, op = '',        name = 'PlaneOrientationSeq',                          comment = ''}
    lTableFromCTP['0020-9128'] = {en = false, op = '',        name = 'TemporalPositionIndex',                        comment = ''}
    lTableFromCTP['0020-9153'] = {en = false, op = '',        name = 'TriggerDelayTime',                             comment = ''}
    lTableFromCTP['0020-9156'] = {en = false, op = '',        name = 'FrameAcquisitionNumber',                       comment = ''}
    lTableFromCTP['0020-9157'] = {en = false, op = '',        name = 'DimensionIndexValues',                         comment = ''}
    lTableFromCTP['0020-9158'] = {en = false, op = '',        name = 'FrameComments',                                comment = ''}
    lTableFromCTP['0020-9161'] = {en = true,  op = 'remove',  name = 'ConcatenationUID',                             comment = ''}
    lTableFromCTP['0020-9162'] = {en = false, op = '',        name = 'InConcatenationNumber',                        comment = ''}
    lTableFromCTP['0020-9163'] = {en = false, op = '',        name = 'InConcatenationTotalNumber',                   comment = ''}
    lTableFromCTP['0020-9164'] = {en = true,  op = 'keep',    name = 'DimensionOrganizationUID',                     comment = 'Per clunie validator - Dicom standard requires keeping this UID used for multiframe enhanced'}
    lTableFromCTP['0020-9165'] = {en = false, op = '',        name = 'DimensionIndexPointer',                        comment = ''}
    lTableFromCTP['0020-9167'] = {en = false, op = '',        name = 'FunctionalGroupSequencePointer',               comment = ''}
    lTableFromCTP['0020-9213'] = {en = false, op = '',        name = 'DimensionIndexPrivateCreator',                 comment = ''}
    lTableFromCTP['0020-9221'] = {en = false, op = '',        name = 'DimensionOrganizationSeq',                     comment = ''}
    lTableFromCTP['0020-9222'] = {en = false, op = '',        name = 'DimensionSeq',                                 comment = ''}
    lTableFromCTP['0020-9228'] = {en = false, op = '',        name = 'ConcatenationFrameOffsetNumber',               comment = ''}
    lTableFromCTP['0020-9238'] = {en = false, op = '',        name = 'FunctionalGroupPrivateCreator',                comment = ''}
    lTableFromCTP['0028-0002'] = {en = false, op = '',        name = 'SamplesPerPixel',                              comment = ''}
    lTableFromCTP['0028-0004'] = {en = false, op = '',        name = 'PhotometricInterpretation',                    comment = ''}
    lTableFromCTP['0028-0006'] = {en = false, op = '',        name = 'PlanarConfiguration',                          comment = ''}
    lTableFromCTP['0028-0008'] = {en = false, op = '',        name = 'NumberOfFrames',                               comment = ''}
    lTableFromCTP['0028-0009'] = {en = false, op = '',        name = 'FrameIncrementPointer',                        comment = ''}
    lTableFromCTP['0028-0010'] = {en = false, op = '',        name = 'Rows',                                         comment = ''}
    lTableFromCTP['0028-0011'] = {en = false, op = '',        name = 'Columns',                                      comment = ''}
    lTableFromCTP['0028-0012'] = {en = false, op = '',        name = 'Planes',                                       comment = ''}
    lTableFromCTP['0028-0014'] = {en = false, op = '',        name = 'UltrasoundColorDataPresent',                   comment = ''}
    lTableFromCTP['0028-0030'] = {en = false, op = '',        name = 'PixelSpacing',                                 comment = ''}
    lTableFromCTP['0028-0031'] = {en = false, op = '',        name = 'ZoomFactor',                                   comment = ''}
    lTableFromCTP['0028-0032'] = {en = false, op = '',        name = 'ZoomCenter',                                   comment = ''}
    lTableFromCTP['0028-0034'] = {en = false, op = '',        name = 'PixelAspectRatio',                             comment = ''}
    lTableFromCTP['0028-0051'] = {en = false, op = '',        name = 'CorrectedImage',                               comment = ''}
    lTableFromCTP['0028-0100'] = {en = false, op = '',        name = 'BitsAllocated',                                comment = ''}
    lTableFromCTP['0028-0101'] = {en = false, op = '',        name = 'BitsStored',                                   comment = ''}
    lTableFromCTP['0028-0102'] = {en = false, op = '',        name = 'HighBit',                                      comment = ''}
    lTableFromCTP['0028-0103'] = {en = false, op = '',        name = 'PixelRepresentation',                          comment = ''}
    lTableFromCTP['0028-0106'] = {en = false, op = '',        name = 'SmallestImagePixelValue',                      comment = ''}
    lTableFromCTP['0028-0107'] = {en = false, op = '',        name = 'LargestImagePixelValue',                       comment = ''}
    lTableFromCTP['0028-0108'] = {en = false, op = '',        name = 'SmallestPixelValueInSeries',                   comment = ''}
    lTableFromCTP['0028-0109'] = {en = false, op = '',        name = 'LargestPixelValueInSeries',                    comment = ''}
    lTableFromCTP['0028-0110'] = {en = false, op = '',        name = 'SmallestImagePixelValueInPlane',               comment = ''}
    lTableFromCTP['0028-0111'] = {en = false, op = '',        name = 'LargestImagePixelValueInPlane',                comment = ''}
    lTableFromCTP['0028-0120'] = {en = false, op = '',        name = 'PixelPaddingValue',                            comment = ''}
    lTableFromCTP['0028-0300'] = {en = false, op = '',        name = 'QualityControlImage',                          comment = ''}
    lTableFromCTP['0028-0301'] = {en = false, op = '',        name = 'BurnedInAnnotation',                           comment = ''}
    lTableFromCTP['0028-1040'] = {en = false, op = '',        name = 'PixelIntensityRelationship',                   comment = ''}
    lTableFromCTP['0028-1041'] = {en = false, op = '',        name = 'PixelIntensityRelationshipSign',               comment = ''}
    lTableFromCTP['0028-1050'] = {en = false, op = '',        name = 'WindowCenter',                                 comment = ''}
    lTableFromCTP['0028-1051'] = {en = false, op = '',        name = 'WindowWidth',                                  comment = ''}
    lTableFromCTP['0028-1052'] = {en = false, op = '',        name = 'RescaleIntercept',                             comment = ''}
    lTableFromCTP['0028-1053'] = {en = false, op = '',        name = 'RescaleSlope',                                 comment = ''}
    lTableFromCTP['0028-1054'] = {en = false, op = '',        name = 'RescaleType',                                  comment = ''}
    lTableFromCTP['0028-1055'] = {en = false, op = '',        name = 'WindowCenterWidthExplanation',                 comment = ''}
    lTableFromCTP['0028-1090'] = {en = false, op = '',        name = 'RecommendedViewingMode',                       comment = ''}
    lTableFromCTP['0028-1101'] = {en = false, op = '',        name = 'RedPaletteColorLUTDescriptor',                 comment = ''}
    lTableFromCTP['0028-1102'] = {en = false, op = '',        name = 'GreenPaletteColorLUTDescriptor',               comment = ''}
    lTableFromCTP['0028-1103'] = {en = false, op = '',        name = 'BluePaletteColorLUTDescriptor',                comment = ''}
    lTableFromCTP['0028-1199'] = {en = true,  op = 'remove',  name = 'PaletteColorLUTUID',                           comment = ''}
    lTableFromCTP['0028-1201'] = {en = false, op = '',        name = 'RedPaletteColorLUTData',                       comment = ''}
    lTableFromCTP['0028-1202'] = {en = false, op = '',        name = 'GreenPaletteColorLUTData',                     comment = ''}
    lTableFromCTP['0028-1203'] = {en = false, op = '',        name = 'BluePaletteColorLUTData',                      comment = ''}
    lTableFromCTP['0028-1214'] = {en = false, op = '',        name = 'LargePaletteColorLUTUid',                      comment = ''}
    lTableFromCTP['0028-1221'] = {en = false, op = '',        name = 'SegmentedRedPaletteColorLUTData',              comment = ''}
    lTableFromCTP['0028-1222'] = {en = false, op = '',        name = 'SegmentedGreenPaletteColorLUTData',            comment = ''}
    lTableFromCTP['0028-1223'] = {en = false, op = '',        name = 'SegmentedBluePaletteColorLUTData',             comment = ''}
    lTableFromCTP['0028-1300'] = {en = false, op = '',        name = 'ImplantPresent',                               comment = ''}
    lTableFromCTP['0028-1350'] = {en = false, op = '',        name = 'PartialView',                                  comment = ''}
    lTableFromCTP['0028-1351'] = {en = false, op = '',        name = 'PartialViewDescription',                       comment = ''}
    lTableFromCTP['0028-2110'] = {en = false, op = '',        name = 'LossyImageCompression',                        comment = ''}
    lTableFromCTP['0028-2112'] = {en = false, op = '',        name = 'LossyImageCompressionRatio',                   comment = ''}
    lTableFromCTP['0028-3000'] = {en = false, op = '',        name = 'ModalityLUTSeq',                               comment = ''}
    lTableFromCTP['0028-3002'] = {en = false, op = '',        name = 'LUTDescriptor',                                comment = ''}
    lTableFromCTP['0028-3003'] = {en = false, op = '',        name = 'LUTExplanation',                               comment = ''}
    lTableFromCTP['0028-3004'] = {en = false, op = '',        name = 'ModalityLUTType',                              comment = ''}
    lTableFromCTP['0028-3006'] = {en = false, op = '',        name = 'LUTData',                                      comment = ''}
    lTableFromCTP['0028-3010'] = {en = false, op = '',        name = 'VOILUTSeq',                                    comment = ''}
    lTableFromCTP['0028-3110'] = {en = false, op = '',        name = 'SoftcopyVOILUTSeq',                            comment = ''}
    lTableFromCTP['0028-4000'] = {en = true,  op = 'remove',  name = 'ImagePresentationComments',                    comment = ''}
    lTableFromCTP['0028-5000'] = {en = false, op = '',        name = 'BiPlaneAcquisitionSeq',                        comment = ''}
    lTableFromCTP['0028-6010'] = {en = false, op = '',        name = 'RepresentativeFrameNumber',                    comment = ''}
    lTableFromCTP['0028-6020'] = {en = false, op = '',        name = 'FrameNumbersOfInterest',                       comment = ''}
    lTableFromCTP['0028-6022'] = {en = false, op = '',        name = 'FrameOfInterestDescription',                   comment = ''}
    lTableFromCTP['0028-6030'] = {en = false, op = '',        name = 'MaskPointer',                                  comment = ''}
    lTableFromCTP['0028-6040'] = {en = false, op = '',        name = 'RWavePointer',                                 comment = ''}
    lTableFromCTP['0028-6100'] = {en = false, op = '',        name = 'MaskSubtractionSeq',                           comment = ''}
    lTableFromCTP['0028-6101'] = {en = false, op = '',        name = 'MaskOperation',                                comment = ''}
    lTableFromCTP['0028-6102'] = {en = false, op = '',        name = 'ApplicableFrameRange',                         comment = ''}
    lTableFromCTP['0028-6110'] = {en = false, op = '',        name = 'MaskFrameNumbers',                             comment = ''}
    lTableFromCTP['0028-6112'] = {en = false, op = '',        name = 'ContrastFrameAveraging',                       comment = ''}
    lTableFromCTP['0028-6114'] = {en = false, op = '',        name = 'MaskSubPixelShift',                            comment = ''}
    lTableFromCTP['0028-6120'] = {en = false, op = '',        name = 'TIDOffset',                                    comment = ''}
    lTableFromCTP['0028-6190'] = {en = false, op = '',        name = 'MaskOperationExplanation',                     comment = ''}
    lTableFromCTP['0028-9001'] = {en = false, op = '',        name = 'DataPointRows',                                comment = ''}
    lTableFromCTP['0028-9002'] = {en = false, op = '',        name = 'DataPointColumns',                             comment = ''}
    lTableFromCTP['0028-9003'] = {en = false, op = '',        name = 'SignalDomain',                                 comment = ''}
    lTableFromCTP['0028-9099'] = {en = false, op = '',        name = 'LargestMonochromePixelValue',                  comment = ''}
    lTableFromCTP['0028-9108'] = {en = false, op = '',        name = 'DataRepresentation',                           comment = ''}
    lTableFromCTP['0028-9110'] = {en = false, op = '',        name = 'PixelMatrixSeq',                               comment = ''}
    lTableFromCTP['0028-9132'] = {en = false, op = '',        name = 'FrameVOILUTSeq',                               comment = ''}
    lTableFromCTP['0028-9145'] = {en = false, op = '',        name = 'PixelValueTransformationSeq',                  comment = ''}
    lTableFromCTP['0028-9235'] = {en = false, op = '',        name = 'SignalDomainRows',                             comment = ''}
    if lFlagKeepSiemensMR then
        lTableFromCTP['0029'] = { en = true,  op = 'groupkeep', name = 'SiemensCSAHeader',                           comment = 'Siemens protocol stuff.  Does capture study date internally'}
    end
    lTableFromCTP['0032-000a'] = {en = false, op = '',        name = 'StudyStatusID',                                comment = ''}
    lTableFromCTP['0032-000c'] = {en = false, op = '',        name = 'StudyPriorityID',                              comment = ''}
    lTableFromCTP['0032-0012'] = {en = true,  op = 'remove',  name = 'StudyIDIssuer',                                comment = ''}
    lTableFromCTP['0032-0032'] = {en = true,  op = 'remove',  name = 'StudyVerifiedDate',                            comment = ''}
    lTableFromCTP['0032-0033'] = {en = false, op = '',        name = 'StudyVerifiedTime',                            comment = ''}
    lTableFromCTP['0032-0034'] = {en = true,  op = 'remove',  name = 'StudyReadDate',                                comment = ''}
    lTableFromCTP['0032-0035'] = {en = false, op = '',        name = 'StudyReadTime',                                comment = ''}
    lTableFromCTP['0032-1000'] = {en = true,  op = 'remove',  name = 'ScheduledStudyStartDate',                      comment = ''}
    lTableFromCTP['0032-1001'] = {en = false, op = '',        name = 'ScheduledStudyStartTime',                      comment = ''}
    lTableFromCTP['0032-1010'] = {en = true,  op = 'remove',  name = 'ScheduledStudyStopDate',                       comment = ''}
    lTableFromCTP['0032-1011'] = {en = false, op = '',        name = 'ScheduledStudyStopTime',                       comment = ''}
    lTableFromCTP['0032-1020'] = {en = true,  op = 'remove',  name = 'ScheduledStudyLocation',                       comment = ''}
    lTableFromCTP['0032-1021'] = {en = true,  op = 'remove',  name = 'ScheduledStudyLocationAET',                    comment = ''}
    lTableFromCTP['0032-1030'] = {en = true,  op = 'remove',  name = 'ReasonforStudy',                               comment = ''}
    lTableFromCTP['0032-1032'] = {en = true,  op = 'remove',  name = 'RequestingPhysician',                          comment = ''}
    lTableFromCTP['0032-1033'] = {en = true,  op = 'remove',  name = 'RequestingService',                            comment = ''}
    lTableFromCTP['0032-1040'] = {en = true,  op = 'remove',  name = 'StudyArrivalDate',                             comment = ''}
    lTableFromCTP['0032-1041'] = {en = false, op = '',        name = 'StudyArrivalTime',                             comment = ''}
    lTableFromCTP['0032-1050'] = {en = true,  op = 'remove',  name = 'StudyCompletionDate',                          comment = ''}
    lTableFromCTP['0032-1051'] = {en = false, op = '',        name = 'StudyCompletionTime',                          comment = ''}
    lTableFromCTP['0032-1055'] = {en = false, op = '',        name = 'StudyComponentStatusID',                       comment = ''}
    lTableFromCTP['0032-1060'] = {en = true,  op = 'remove',  name = 'RequestedProcedureDescription',                comment = ''}
    lTableFromCTP['0032-1064'] = {en = true,  op = 'remove',  name = 'RequestedProcedureCodeSeq',                    comment = ''}
    lTableFromCTP['0032-1070'] = {en = true,  op = 'remove',  name = 'RequestedContrastAgent',                       comment = ''}
    lTableFromCTP['0032-4000'] = {en = true,  op = 'remove',  name = 'StudyComments',                                comment = ''}
    lTableFromCTP['0038-0004'] = {en = false, op = '',        name = 'RefPatientAliasSeq',                           comment = ''}
    lTableFromCTP['0038-0008'] = {en = false, op = '',        name = 'VisitStatusID',                                comment = ''}
    lTableFromCTP['0038-0010'] = {en = true,  op = 'remove',  name = 'AdmissionID',                                  comment = ''}
    lTableFromCTP['0038-0011'] = {en = true,  op = 'remove',  name = 'IssuerOfAdmissionID',                          comment = ''}
    lTableFromCTP['0038-0016'] = {en = false, op = '',        name = 'RouteOfAdmissions',                            comment = ''}
    lTableFromCTP['0038-001a'] = {en = true,  op = 'remove',  name = 'ScheduledAdmissionDate',                       comment = ''}
    lTableFromCTP['0038-001b'] = {en = false, op = '',        name = 'ScheduledAdmissionTime',                       comment = ''}
    lTableFromCTP['0038-001c'] = {en = true,  op = 'remove',  name = 'ScheduledDischargeDate',                       comment = ''}
    lTableFromCTP['0038-001d'] = {en = false, op = '',        name = 'ScheduledDischargeTime',                       comment = ''}
    lTableFromCTP['0038-001e'] = {en = true,  op = 'remove',  name = 'ScheduledPatientInstitutionResidence',         comment = ''}
    lTableFromCTP['0038-0020'] = {en = true,  op = 'remove',  name = 'AdmittingDate',                                comment = ''}
    lTableFromCTP['0038-0021'] = {en = true,  op = 'remove',  name = 'AdmittingTime',                                comment = ''}
    lTableFromCTP['0038-0030'] = {en = true,  op = 'remove',  name = 'DischargeDate',                                comment = ''}
    lTableFromCTP['0038-0032'] = {en = false, op = '',        name = 'DischargeTime',                                comment = ''}
    lTableFromCTP['0038-0040'] = {en = true,  op = 'remove',  name = 'DischargeDiagnosisDescription',                comment = ''}
    lTableFromCTP['0038-0044'] = {en = false, op = '',        name = 'DischargeDiagnosisCodeSeq',                    comment = ''}
    lTableFromCTP['0038-0050'] = {en = true,  op = 'remove',  name = 'SpecialNeeds',                                 comment = ''}
    lTableFromCTP['0038-0060'] = {en = true,  op = 'remove',  name = 'ServiceEpisodeID',                             comment = ''}
    lTableFromCTP['0038-0061'] = {en = true,  op = 'remove',  name = 'IssuerOfServiceEpisodeId',                     comment = ''}
    lTableFromCTP['0038-0062'] = {en = true,  op = 'remove',  name = 'ServiceEpisodeDescription',                    comment = ''}
    lTableFromCTP['0038-0300'] = {en = true,  op = 'remove',  name = 'CurrentPatientLocation',                       comment = ''}
    lTableFromCTP['0038-0400'] = {en = true,  op = 'remove',  name = 'PatientInstitutionResidence',                  comment = ''}
    lTableFromCTP['0038-0500'] = {en = true,  op = 'remove',  name = 'PatientState',                                 comment = ''}
    lTableFromCTP['0038-1234'] = {en = true,  op = 'remove',  name = 'ReferencedPatientAliasSeq',                    comment = ''}
    lTableFromCTP['0038-4000'] = {en = true,  op = 'remove',  name = 'VisitComments',                                comment = ''}
    lTableFromCTP['003a-0004'] = {en = false, op = '',        name = 'WaveformOriginality',                          comment = ''}
    lTableFromCTP['003a-0005'] = {en = false, op = '',        name = 'NumberOfWaveformChannels',                     comment = ''}
    lTableFromCTP['003a-0010'] = {en = false, op = '',        name = 'NumberOfWaveformSamples',                      comment = ''}
    lTableFromCTP['003a-001a'] = {en = false, op = '',        name = 'SamplingFrequency',                            comment = ''}
    lTableFromCTP['003a-0020'] = {en = false, op = '',        name = 'MultiplexGroupLabel',                          comment = ''}
    lTableFromCTP['003a-0200'] = {en = false, op = '',        name = 'ChannelDefinitionSeq',                         comment = ''}
    lTableFromCTP['003a-0202'] = {en = false, op = '',        name = 'WaveformChannelNumber',                        comment = ''}
    lTableFromCTP['003a-0203'] = {en = false, op = '',        name = 'ChannelLabel',                                 comment = ''}
    lTableFromCTP['003a-0205'] = {en = false, op = '',        name = 'ChannelStatus',                                comment = ''}
    lTableFromCTP['003a-0208'] = {en = false, op = '',        name = 'ChannelSourceSeq',                             comment = ''}
    lTableFromCTP['003a-0209'] = {en = false, op = '',        name = 'ChannelSourceModifiersSeq',                    comment = ''}
    lTableFromCTP['003a-020a'] = {en = false, op = '',        name = 'SourceWaveformSeq',                            comment = ''}
    lTableFromCTP['003a-020c'] = {en = false, op = '',        name = 'ChannelDerivationDescription',                 comment = ''}
    lTableFromCTP['003a-0210'] = {en = false, op = '',        name = 'ChannelSensitivity',                           comment = ''}
    lTableFromCTP['003a-0211'] = {en = false, op = '',        name = 'ChannelSensitivityUnitsSeq',                   comment = ''}
    lTableFromCTP['003a-0212'] = {en = false, op = '',        name = 'ChannelSensitivityCorrectionFactor',           comment = ''}
    lTableFromCTP['003a-0213'] = {en = false, op = '',        name = 'ChannelBaseline',                              comment = ''}
    lTableFromCTP['003a-0214'] = {en = false, op = '',        name = 'ChannelTimeSkew',                              comment = ''}
    lTableFromCTP['003a-0215'] = {en = false, op = '',        name = 'ChannelSampleSkew',                            comment = ''}
    lTableFromCTP['003a-0218'] = {en = false, op = '',        name = 'ChannelOffset',                                comment = ''}
    lTableFromCTP['003a-021a'] = {en = false, op = '',        name = 'WaveformBitsStored',                           comment = ''}
    lTableFromCTP['003a-0220'] = {en = false, op = '',        name = 'FilterLowFrequency',                           comment = ''}
    lTableFromCTP['003a-0221'] = {en = false, op = '',        name = 'FilterHighFrequency',                          comment = ''}
    lTableFromCTP['003a-0222'] = {en = false, op = '',        name = 'NotchFilterFrequency',                         comment = ''}
    lTableFromCTP['003a-0223'] = {en = false, op = '',        name = 'NotchFilterBandwidth',                         comment = ''}
    lTableFromCTP['0040-0001'] = {en = true,  op = 'remove',  name = 'ScheduledStationAET',                          comment = ''}
    lTableFromCTP['0040-0002'] = {en = true,  op = 'remove',  name = 'SPSStartDate',                                 comment = ''}
    lTableFromCTP['0040-0003'] = {en = false, op = '',        name = 'SPSStartTime',                                 comment = ''}
    lTableFromCTP['0040-0004'] = {en = true,  op = 'remove',  name = 'SPSEndDate',                                   comment = ''}
    lTableFromCTP['0040-0005'] = {en = false, op = '',        name = 'SPSEndTime',                                   comment = ''}
    lTableFromCTP['0040-0006'] = {en = true,  op = 'remove',  name = 'ScheduledPerformingPhysicianName',             comment = ''}
    lTableFromCTP['0040-0007'] = {en = true,  op = 'remove',  name = 'ScheduledProcedureStepDescription',            comment = ''}
    lTableFromCTP['0040-0008'] = {en = true,  op = 'remove',  name = 'ScheduledProtocolCodeSeq',                     comment = ''}
    lTableFromCTP['0040-0009'] = {en = false, op = '',        name = 'SPSID',                                        comment = ''}
    lTableFromCTP['0040-000b'] = {en = true,  op = 'remove',  name = '',                                             comment = ''}
    lTableFromCTP['0040-0010'] = {en = true,  op = 'remove',  name = 'ScheduledStationName',                         comment = ''}
    lTableFromCTP['0040-0011'] = {en = true,  op = 'remove',  name = 'SPSLocation',                                  comment = ''}
    lTableFromCTP['0040-0012'] = {en = true,  op = 'remove',  name = 'PreMedication',                                comment = ''}
    lTableFromCTP['0040-0020'] = {en = false, op = '',        name = 'SPSStatus',                                    comment = ''}
    lTableFromCTP['0040-0100'] = {en = false, op = '',        name = 'SPSSeq',                                       comment = ''}
    lTableFromCTP['0040-0220'] = {en = false, op = '',        name = 'RefNonImageCompositeSOPInstanceSeq',           comment = ''}
    lTableFromCTP['0040-0241'] = {en = true,  op = 'remove',  name = 'PerformedStationAET',                          comment = ''}
    lTableFromCTP['0040-0242'] = {en = true,  op = 'remove',  name = 'PerformedStationName',                         comment = ''}
    lTableFromCTP['0040-0243'] = {en = true,  op = 'remove',  name = 'PerformedLocation',                            comment = ''}
    lTableFromCTP['0040-0244'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepStartDate',              comment = ''}
    lTableFromCTP['0040-0245'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepStartTime',              comment = ''}
    lTableFromCTP['0040-0248'] = {en = true,  op = 'remove',  name = 'PerformedStationNameCodeSeq',                  comment = ''}
    lTableFromCTP['0040-0250'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepEndDate',                comment = ''}
    lTableFromCTP['0040-0251'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepEndTime',                comment = ''}
    lTableFromCTP['0040-0252'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepStatus',                 comment = ''}
    lTableFromCTP['0040-0253'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepID',                     comment = ''}
    lTableFromCTP['0040-0254'] = {en = true,  op = 'remove',  name = 'PerformedProcedureStepDescription',            comment = ''}
    lTableFromCTP['0040-0255'] = {en = true,  op = 'remove',  name = 'PerformedProcedureTypeDescription',            comment = ''}
    lTableFromCTP['0040-0260'] = {en = true,  op = 'remove',  name = 'PerformedProtocolCodeSeq',                     comment = ''}
    lTableFromCTP['0040-0270'] = {en = false, op = '',        name = 'ScheduledStepAttributesSeq',                   comment = ''}
    lTableFromCTP['0040-0275'] = {en = true,  op = 'remove',  name = 'RequestAttributesSeq',                         comment = ''}
    lTableFromCTP['0040-0280'] = {en = true,  op = 'remove',  name = 'PPSComments',                                  comment = ''}
    lTableFromCTP['0040-0281'] = {en = false, op = '',        name = 'PPSDiscontinuationReasonCodeSeq',              comment = ''}
    lTableFromCTP['0040-0293'] = {en = false, op = '',        name = 'QuantitySeq',                                  comment = ''}
    lTableFromCTP['0040-0294'] = {en = false, op = '',        name = 'Quantity',                                     comment = ''}
    lTableFromCTP['0040-0295'] = {en = false, op = '',        name = 'MeasuringUnitsSeq',                            comment = ''}
    lTableFromCTP['0040-0296'] = {en = false, op = '',        name = 'BillingItemSeq',                               comment = ''}
    lTableFromCTP['0040-0300'] = {en = false, op = '',        name = 'TotalTimeOfFluoroscopy',                       comment = ''}
    lTableFromCTP['0040-0301'] = {en = false, op = '',        name = 'TotalNumberOfExposures',                       comment = ''}
    lTableFromCTP['0040-0302'] = {en = false, op = '',        name = 'EntranceDose',                                 comment = ''}
    lTableFromCTP['0040-0303'] = {en = false, op = '',        name = 'ExposedArea',                                  comment = ''}
    lTableFromCTP['0040-0306'] = {en = false, op = '',        name = 'DistanceSourceToEntrance',                     comment = ''}
    lTableFromCTP['0040-0307'] = {en = false, op = '',        name = 'DistanceSourceToSupport',                      comment = ''}
    lTableFromCTP['0040-030e'] = {en = true,  op = 'remove',  name = 'RETIRED_ExposureDoseSequence',                 comment = 'Something embeds stuff here, maybe when loading another institutions pacs into our pacs?'}
    lTableFromCTP['0040-0310'] = {en = false, op = '',        name = 'CommentsOnRadiationDose',                      comment = ''}
    lTableFromCTP['0040-0312'] = {en = false, op = '',        name = 'XRayOutput',                                   comment = ''}
    lTableFromCTP['0040-0314'] = {en = false, op = '',        name = 'HalfValueLayer',                               comment = ''}
    lTableFromCTP['0040-0316'] = {en = false, op = '',        name = 'OrganDose',                                    comment = ''}
    lTableFromCTP['0040-0318'] = {en = false, op = '',        name = 'OrganExposed',                                 comment = ''}
    lTableFromCTP['0040-0320'] = {en = false, op = '',        name = 'BillingProcedureStepSeq',                      comment = ''}
    lTableFromCTP['0040-0321'] = {en = false, op = '',        name = 'FilmConsumptionSeq',                           comment = ''}
    lTableFromCTP['0040-0324'] = {en = false, op = '',        name = 'BillingSuppliesAndDevicesSeq',                 comment = ''}
    lTableFromCTP['0040-0330'] = {en = false, op = '',        name = 'RefProcedureStepSeq',                          comment = ''}
    lTableFromCTP['0040-0340'] = {en = false, op = '',        name = 'PerformedSeriesSeq',                           comment = ''}
    lTableFromCTP['0040-0400'] = {en = false, op = '',        name = 'SPSComments',                                  comment = ''}
    lTableFromCTP['0040-050a'] = {en = false, op = '',        name = 'SpecimenAccessionNumber',                      comment = ''}
    lTableFromCTP['0040-0550'] = {en = false, op = '',        name = 'SpecimenSeq',                                  comment = ''}
    lTableFromCTP['0040-0551'] = {en = false, op = '',        name = 'SpecimenIdentifier',                           comment = ''}
    lTableFromCTP['0040-0555'] = {en = true, op = 'emptyseq', name = 'AcquisitionContextSequence',                   comment = 'Per Clunie, must exist but can be empty'}
    lTableFromCTP['0040-0556'] = {en = false, op = '',        name = 'AcquisitionContextDescription',                comment = ''}
    lTableFromCTP['0040-059a'] = {en = false, op = '',        name = 'SpecimenTypeCodeSeq',                          comment = ''}
    lTableFromCTP['0040-06fa'] = {en = false, op = '',        name = 'SlideIdentifier',                              comment = ''}
    lTableFromCTP['0040-071a'] = {en = false, op = '',        name = 'ImageCenterPointCoordinatesSeq',               comment = ''}
    lTableFromCTP['0040-072a'] = {en = false, op = '',        name = 'XOffsetInSlideCoordinateSystem',               comment = ''}
    lTableFromCTP['0040-073a'] = {en = false, op = '',        name = 'YOffsetInSlideCoordinateSystem',               comment = ''}
    lTableFromCTP['0040-074a'] = {en = false, op = '',        name = 'ZOffsetInSlideCoordinateSystem',               comment = ''}
    lTableFromCTP['0040-08d8'] = {en = false, op = '',        name = 'PixelSpacingSeq',                              comment = ''}
    lTableFromCTP['0040-08da'] = {en = false, op = '',        name = 'CoordinateSystemAxisCodeSeq',                  comment = ''}
    lTableFromCTP['0040-08ea'] = {en = false, op = '',        name = 'MeasurementUnitsCodeSeq',                      comment = ''}
    lTableFromCTP['0040-1001'] = {en = true,  op = 'empty',   name = 'RequestedProcedureID',                         comment = ''}
    lTableFromCTP['0040-1002'] = {en = false, op = '',        name = 'ReasonForTheRequestedProcedure',               comment = ''}
    lTableFromCTP['0040-1003'] = {en = false, op = '',        name = 'RequestedProcedurePriority',                   comment = ''}
    lTableFromCTP['0040-1004'] = {en = true,  op = 'remove',  name = 'PatientTransportArrangements',                 comment = ''}
    lTableFromCTP['0040-1005'] = {en = true,  op = 'remove',  name = 'RequestedProcedureLocation',                   comment = ''}
    lTableFromCTP['0040-1008'] = {en = false, op = '',        name = 'ConfidentialityCode',                          comment = ''}
    lTableFromCTP['0040-1009'] = {en = false, op = '',        name = 'ReportingPriority',                            comment = ''}
    lTableFromCTP['0040-1010'] = {en = true,  op = 'remove',  name = 'NamesOfIntendedRecipientsOfResults',           comment = ''}
    lTableFromCTP['0040-1011'] = {en = true,  op = 'remove',  name = 'IntendedRecipientsOfResultsIDSequence',        comment = ''}
    lTableFromCTP['0040-1102'] = {en = true,  op = 'remove',  name = 'PersonAddress',                                comment = ''}
    lTableFromCTP['0040-1103'] = {en = true,  op = 'remove',  name = 'PersonTelephoneNumbers',                       comment = ''}
    lTableFromCTP['0040-1400'] = {en = true,  op = 'remove',  name = 'RequestedProcedureComments',                   comment = ''}
    lTableFromCTP['0040-2001'] = {en = true,  op = 'remove',  name = 'ReasonForTheImagingServiceRequest',            comment = ''}
    lTableFromCTP['0040-2004'] = {en = true,  op = 'remove',  name = 'IssueDateOfImagingServiceRequest',             comment = ''}
    lTableFromCTP['0040-2005'] = {en = false, op = '',        name = 'IssueTimeOfImagingServiceRequest',             comment = ''}
    lTableFromCTP['0040-2008'] = {en = true,  op = 'remove',  name = 'OrderEnteredBy',                               comment = ''}
    lTableFromCTP['0040-2009'] = {en = true,  op = 'remove',  name = 'OrderEntererLocation',                         comment = ''}
    lTableFromCTP['0040-2010'] = {en = true,  op = 'remove',  name = 'OrderCallbackPhoneNumber',                     comment = ''}
    lTableFromCTP['0040-2016'] = {en = true,  op = 'remove',  name = 'PlacerOrderNumber',                            comment = ''}
    lTableFromCTP['0040-2017'] = {en = true,  op = 'remove',  name = 'FillerOrderNumber',                            comment = ''}
    lTableFromCTP['0040-2400'] = {en = true,  op = 'remove',  name = 'ImagingServiceRequestComments',                comment = ''}
    lTableFromCTP['0040-3001'] = {en = true,  op = 'remove',  name = 'ConfidentialityPatientData',                   comment = ''}
    lTableFromCTP['0040-4023'] = {en = true,  op = 'remove',  name = 'RefGenPurposeSchedProcStepTransUID',           comment = ''}
    lTableFromCTP['0040-4025'] = {en = true,  op = 'remove',  name = 'ScheduledStationNameCodeSeq',                  comment = ''}
    lTableFromCTP['0040-4027'] = {en = true,  op = 'remove',  name = 'ScheduledStationGeographicLocCodeSeq',         comment = ''}
    lTableFromCTP['0040-4030'] = {en = true,  op = 'remove',  name = 'PerformedStationGeoLocCodeSeq',                comment = ''}
    lTableFromCTP['0040-4034'] = {en = true,  op = 'remove',  name = 'ScheduledHumanPerformersSeq',                  comment = ''}
    lTableFromCTP['0040-4035'] = {en = true,  op = 'remove',  name = 'ActualHumanPerformersSequence',                comment = ''}
    lTableFromCTP['0040-4036'] = {en = true,  op = 'remove',  name = 'HumanPerformersOrganization',                  comment = ''}
    lTableFromCTP['0040-4037'] = {en = true,  op = 'remove',  name = 'HumanPerformersName',                          comment = ''}
    lTableFromCTP['0040-8302'] = {en = false, op = '',        name = 'EntranceDoseInmGy',                            comment = ''}
    lTableFromCTP['0040-9096'] = {en = false, op = '',        name = 'RealWorldValueMappingSeq',                     comment = ''}
    lTableFromCTP['0040-9210'] = {en = false, op = '',        name = 'LUTLabel',                                     comment = ''}
    lTableFromCTP['0040-9211'] = {en = false, op = '',        name = 'RealWorldValueLUTLastValueMappedUS',           comment = ''}
    lTableFromCTP['0040-9212'] = {en = false, op = '',        name = 'RealWorldValueLUTData',                        comment = ''}
    lTableFromCTP['0040-9216'] = {en = false, op = '',        name = 'RealWorldValueLUTFirstValueMappedUS',          comment = ''}
    lTableFromCTP['0040-9224'] = {en = false, op = '',        name = 'RealWorldValueIntercept',                      comment = ''}
    lTableFromCTP['0040-9225'] = {en = false, op = '',        name = 'RealWorldValueSlope',                          comment = ''}
    lTableFromCTP['0040-a010'] = {en = false, op = '',        name = 'RelationshipType',                             comment = ''}
    lTableFromCTP['0040-a027'] = {en = true,  op = 'remove',  name = 'VerifyingOrganization',                        comment = ''}
    lTableFromCTP['0040-a030'] = {en = true,  op = 'remove',  name = 'VerificationDateTime',                         comment = ''}
    lTableFromCTP['0040-a032'] = {en = true,  op = 'remove',  name = 'ObservationDateTime',                          comment = ''}
    lTableFromCTP['0040-a040'] = {en = false, op = '',        name = 'ValueType',                                    comment = ''}
    lTableFromCTP['0040-a043'] = {en = false, op = '',        name = 'ConceptNameCodeSeq',                           comment = ''}
    lTableFromCTP['0040-a050'] = {en = false, op = '',        name = 'ContinuityOfContent',                          comment = ''}
    lTableFromCTP['0040-a073'] = {en = false, op = '',        name = 'VerifyingObserverSeq',                         comment = ''}
    lTableFromCTP['0040-a075'] = {en = true,  op = 'remove',  name = 'VerifyingObserverName',                        comment = ''}
    lTableFromCTP['0040-a078'] = {en = true,  op = 'remove',  name = 'AuthorObserverSequence',                       comment = ''}
    lTableFromCTP['0040-a07a'] = {en = true,  op = 'remove',  name = 'ParticipantSequence',                          comment = ''}
    lTableFromCTP['0040-a07c'] = {en = true,  op = 'remove',  name = 'CustodialOrganizationSeq',                     comment = ''}
    lTableFromCTP['0040-a088'] = {en = true,  op = 'remove',  name = 'VerifyingObserverIdentificationCodeSeq',       comment = ''}
    lTableFromCTP['0040-a0b0'] = {en = false, op = '',        name = 'RefWaveformChannels',                          comment = ''}
    lTableFromCTP['0040-a120'] = {en = true,  op = 'remove',  name = 'DateTime',                                     comment = ''}
    lTableFromCTP['0040-a121'] = {en = true,  op = 'remove',  name = 'Date',                                         comment = ''}
    lTableFromCTP['0040-a122'] = {en = false, op = '',        name = 'Time',                                         comment = ''}
    lTableFromCTP['0040-a123'] = {en = true,  op = 'remove',  name = 'PersonName',                                   comment = ''}
    lTableFromCTP['0040-a124'] = {en = true,  op = 'remove',  name = 'UID',                                          comment = ''}
    lTableFromCTP['0040-a130'] = {en = false, op = '',        name = 'TemporalRangeType',                            comment = ''}
    lTableFromCTP['0040-a132'] = {en = false, op = '',        name = 'RefSamplePositions',                           comment = ''}
    lTableFromCTP['0040-a136'] = {en = false, op = '',        name = 'RefFrameNumbers',                              comment = ''}
    lTableFromCTP['0040-a138'] = {en = false, op = '',        name = 'RefTimeOffsets',                               comment = ''}
    lTableFromCTP['0040-a13a'] = {en = true,  op = 'remove',  name = 'RefDatetime',                                  comment = ''}
    lTableFromCTP['0040-a160'] = {en = false, op = '',        name = 'TextValue',                                    comment = ''}
    lTableFromCTP['0040-a168'] = {en = false, op = '',        name = 'ConceptCodeSeq',                               comment = ''}
    lTableFromCTP['0040-a180'] = {en = false, op = '',        name = 'AnnotationGroupNumber',                        comment = ''}
    lTableFromCTP['0040-a195'] = {en = false, op = '',        name = 'ModifierCodeSeq',                              comment = ''}
    lTableFromCTP['0040-a300'] = {en = false, op = '',        name = 'MeasuredValueSeq',                             comment = ''}
    lTableFromCTP['0040-a30a'] = {en = false, op = '',        name = 'NumericValue',                                 comment = ''}
    lTableFromCTP['0040-a360'] = {en = false, op = '',        name = 'PredecessorDocumentsSeq',                      comment = ''}
    lTableFromCTP['0040-a370'] = {en = false, op = '',        name = 'RefRequestSeq',                                comment = ''}
    lTableFromCTP['0040-a372'] = {en = false, op = '',        name = 'PerformedProcedureCodeSeq',                    comment = ''}
    lTableFromCTP['0040-a375'] = {en = false, op = '',        name = 'CurrentRequestedProcedureEvidenceSeq',         comment = ''}
    lTableFromCTP['0040-a385'] = {en = false, op = '',        name = 'PertinentOtherEvidenceSeq',                    comment = ''}
    lTableFromCTP['0040-a491'] = {en = false, op = '',        name = 'CompletionFlag',                               comment = ''}
    lTableFromCTP['0040-a492'] = {en = false, op = '',        name = 'CompletionFlagDescription',                    comment = ''}
    lTableFromCTP['0040-a493'] = {en = false, op = '',        name = 'VerificationFlag',                             comment = ''}
    lTableFromCTP['0040-a504'] = {en = false, op = '',        name = 'ContentTemplateSeq',                           comment = ''}
    lTableFromCTP['0040-a525'] = {en = false, op = '',        name = 'IdenticalDocumentsSeq',                        comment = ''}
    lTableFromCTP['0040-a730'] = {en = true,  op = 'remove',  name = 'ContentSeq',                                   comment = ''}
    lTableFromCTP['0040-b020'] = {en = false, op = '',        name = 'AnnotationSeq',                                comment = ''}
    lTableFromCTP['0040-db00'] = {en = false, op = '',        name = 'TemplateIdentifier',                           comment = ''}
    lTableFromCTP['0040-db06'] = {en = false, op = '',        name = 'TemplateVersion',                              comment = ''}
    lTableFromCTP['0040-db07'] = {en = false, op = '',        name = 'TemplateLocalVersion',                         comment = ''}
    lTableFromCTP['0040-db0b'] = {en = false, op = '',        name = 'TemplateExtensionFlag',                        comment = ''}
    lTableFromCTP['0040-db0c'] = {en = true,  op = 'remove',  name = 'TemplateExtensionOrganizationUID',             comment = ''}
    lTableFromCTP['0040-db0d'] = {en = true,  op = 'remove',  name = 'TemplateExtensionCreatorUID',                  comment = ''}
    lTableFromCTP['0040-db73'] = {en = false, op = '',        name = 'RefContentItemIdentifier',                     comment = ''}
    if lFlagKeepSiemensMR then
        lTableFromCTP['0051'] = { en = true,  op = 'groupkeep', name = 'SiemensMRHeader',                            comment = 'Siemens protocol stuff.  Does capture study date internally'}
    end
    lTableFromCTP['0060-3000'] = {en = true,  op = 'remove',  name = 'OverlayData',                                  comment = ''}
    lTableFromCTP['0060-4000'] = {en = true,  op = 'remove',  name = 'OverlayComments',                              comment = ''}
    lTableFromCTP['0070-031a'] = {en = true,  op = 'remove',  name = 'FiducialUID',                                  comment = ''}
    lTableFromCTP['0088-0140'] = {en = true,  op = 'remove',  name = 'StorageMediaFilesetUID',                       comment = ''}
    lTableFromCTP['0088-0200'] = {en = true,  op = 'remove',  name = 'IconImageSequence',                            comment = ''}
    lTableFromCTP['0088-0906'] = {en = true,  op = 'remove',  name = 'TopicSubject',                                 comment = ''}
    lTableFromCTP['0088-0910'] = {en = true,  op = 'remove',  name = 'TopicAuthor',                                  comment = ''}
    lTableFromCTP['0088-0912'] = {en = true,  op = 'remove',  name = 'TopicKeyWords',                                comment = ''}
    lTableFromCTP['0400-0100'] = {en = true,  op = 'remove',  name = 'DigitalSignatureUID',                          comment = ''}
    lTableFromCTP['0400-0561'] = {en = true,  op = 'remove',  name = 'OriginalAttributesSequence',                   comment = 'yet another PHI location snuck in by importing foreign DICOM'}
    lTableFromCTP['2030-0020'] = {en = true,  op = 'remove',  name = 'TextString',                                   comment = ''}
    lTableFromCTP['3006-0024'] = {en = true,  op = 'remove',  name = 'ReferencedFrameOfReferenceUID',                comment = ''}
    lTableFromCTP['3006-00c2'] = {en = true,  op = 'remove',  name = 'RelatedFrameOfReferenceUID',                   comment = ''}
    lTableFromCTP['300a-0013'] = {en = true,  op = 'remove',  name = 'DoseReferenceUID',                             comment = ''}
    lTableFromCTP['4000-0010'] = {en = true,  op = 'remove',  name = 'Arbitrary',                                    comment = ''}
    lTableFromCTP['4000-4000'] = {en = true,  op = 'remove',  name = 'TextComments',                                 comment = ''}
    lTableFromCTP['4008-0042'] = {en = true,  op = 'remove',  name = 'ResultsIDIssuer',                              comment = ''}
    lTableFromCTP['4008-0102'] = {en = true,  op = 'remove',  name = 'InterpretationRecorder',                       comment = ''}
    lTableFromCTP['4008-010a'] = {en = true,  op = 'remove',  name = 'InterpretationTranscriber',                    comment = ''}
    lTableFromCTP['4008-010b'] = {en = true,  op = 'remove',  name = 'InterpretationText',                           comment = ''}
    lTableFromCTP['4008-010c'] = {en = true,  op = 'remove',  name = 'InterpretationAuthor',                         comment = ''}
    lTableFromCTP['4008-0111'] = {en = true,  op = 'remove',  name = 'InterpretationApproverSequence',               comment = ''}
    lTableFromCTP['4008-0114'] = {en = true,  op = 'remove',  name = 'PhysicianApprovingInterpretation',             comment = ''}
    lTableFromCTP['4008-0115'] = {en = true,  op = 'remove',  name = 'InterpretationDiagnosisDescription',           comment = ''}
    lTableFromCTP['4008-0118'] = {en = true,  op = 'remove',  name = 'ResultsDistributionListSeq',                   comment = ''}
    lTableFromCTP['4008-0119'] = {en = true,  op = 'remove',  name = 'DistributionName',                             comment = ''}
    lTableFromCTP['4008-011a'] = {en = true,  op = 'remove',  name = 'DistributionAddress',                          comment = ''}
    lTableFromCTP['4008-0202'] = {en = true,  op = 'remove',  name = 'InterpretationIdIssuer',                       comment = ''}
    lTableFromCTP['4008-0300'] = {en = true,  op = 'remove',  name = 'Impressions',                                  comment = ''}
    lTableFromCTP['4008-4000'] = {en = true,  op = 'remove',  name = 'ResultComments',                               comment = ''}
    lTableFromCTP['50..']      = {en = true,  op = 'groupremovere', name = 'Curves',                                 comment = 'Curve data.  Regex permitted in group spec.'}
    lTableFromCTP['60..']      = {en = true,  op = 'groupremovere', name = 'Overlays',                               comment = 'Overlays might have burned in PHI.  Regex permitted in group spec.'}
    if lFlagHologic then
        lTableFromCTP['7e01'] = { en = true,  op = 'groupkeep', name = 'HologicHeader',                            comment = 'Siemens/Hologic protocol stuff.  Does capture study date internally'}
    end
    lTableFromCTP['fffa-fffa'] = {en = true,  op = 'remove',  name = 'DigitalSignaturesSeq',                         comment = ''}
    lTableFromCTP['fffc-fffc'] = {en = true,  op = 'remove',  name = 'DataSetTrailingPadding',                       comment = ''}

    local lTagHandling = { ['keep'] = {}, ['remove'] = {} }
    local lFoundPrivateAddress = false
    local lFoundPrivateGroups = false
    local lGroup, lElement
    for lTag, lValue in pairs(lTableFromCTP) do
        if lValue.en then
            if not lTagHandling[lValue.op] then
                lTagHandling[lValue.op] = {}
            end
            if lValue.op == 'groupkeep' then
                if ((tonumber(lTag,16) % 2) == 1) then
                    lFoundPrivateGroups = true
                end
            else
                if lValue.op ~= 'groupremovere' then
                    _, _, lGroup, lElement = string.find(lTag, "([^%-]+)%-([^%-]+)")
                    if ((tonumber(lGroup,16) % 2) == 1) then
                        lFoundPrivateAddress = true
                    end
                end
            end
            lTagHandling[lValue.op][lTag] = true
        end
    end

    local lTagHandlingList = { ['keep'] = {}, ['remove'] = {} }
    for lTag, lValue in pairs(lTagHandling['keep']) do
        table.insert(lTagHandlingList['keep'], lTag)
    end
    for lTag, lValue in pairs(lTagHandling['remove']) do
        table.insert(lTagHandlingList['remove'], lTag)
    end
    if lTagHandling['groupkeep'] then
        lTagHandlingList['groupkeep'] = {}
        for lTag, lValue in pairs(lTagHandling['groupkeep']) do
            table.insert(lTagHandlingList['groupkeep'], lTag)
        end
    end
    if lTagHandling['groupremovere'] then
        lTagHandlingList['groupremovere'] = {}
        for lTag, lValue in pairs(lTagHandling['groupremovere']) do
            table.insert(lTagHandlingList['groupremovere'], lTag)
        end
    end

    lTagHandling['KeepSomePrivate'] = lFoundPrivateGroups or lFoundPrivateAddress
   
    return lTagHandling, lTagHandlingList

end

-- ======================================================
function AnonymizeInstances(aLevel, aoLevelID, aFlagFirstCall, 
                            aSQLpid,adPatientIDAnon,
                            aSQLsiuid, adStudyInstanceUIDAnon, aPatientIDModifier)

    if gIndent then gIndent=gIndent+3 else gIndent=0 end
    if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
    gIndent = gIndent + 3
    local lTime0 = os.time()
    local lFlagByStudy = string.find(aLevel, 'Study')

    -- Load tag keep/remove info
    local lTagHandling, lTagHandlingList
    -- lTagHandling, lTagHandlingList = BaseTagHandling()
    local lResults = ParseJson(RestApiGet('/base_tag_handling_lua', false))
    lTagHandling = lResults['TagHandling']
    lTagHandlingList = lResults['TagHandlingList']
 
    -- Capture all UID values for all instances and collect keep/remove data
    if gVerbose then print(string.rep(' ', gIndent) .. 'Capturing UID for all instances') end
    local lTagsEncountered = {}
    local lTagsToKeep = {}
    local lTagsToRemove = {}
    if aFlagFirstCall then
        gTopLevelTagToKeep = {}
        gKeptUID = {}
    end
    local loLevelInstancesMeta
    local lRecurseProprietary, lRecurseRemove, lRecurseGroupKeep, lRecurseGroupRemoveRe
    if lFlagByStudy then
        loLevelInstancesMeta = ParseJson(RestApiGet('/studies/' .. aoLevelID .. '/instances', false))
        lRecurseProprietary = ParseJson(RestApiGet('/studies/' .. aoLevelID .. '/odd_group_recursive_search', false))
        lRecurseRemove = ParseJson(RestApiPost('/studies/' .. aoLevelID .. '/group_element_recursive_search', DumpJson(lTagHandlingList['remove']), false))
        if lTagHandling['groupkeep'] then
            lRecurseGroupKeep = ParseJson(RestApiPost('/studies/' .. aoLevelID .. '/group_recursive_search', DumpJson(lTagHandlingList['groupkeep']), false))
        end
        if lTagHandling['groupremovere'] then
            lRecurseGroupRemoveRe = ParseJson(RestApiPost('/studies/' .. aoLevelID .. '/group_regexp_recursive_search', DumpJson(lTagHandlingList['groupremovere']), false))
        else
            lRecurseGroupRemoveRe = nil
        end
    else
        loLevelInstancesMeta = ParseJson(RestApiGet('/series/' .. aoLevelID .. '/instances', false))
        lRecurseProprietary = ParseJson(RestApiGet('/series/' .. aoLevelID .. '/odd_group_recursive_search', false))
        lRecurseRemove = ParseJson(RestApiPost('/series/' .. aoLevelID .. '/group_element_recursive_search', DumpJson(lTagHandlingList['remove']), false))
        if lTagHandling['groupkeep'] then
            lRecurseGroupKeep = ParseJson(RestApiPost('/series/' .. aoLevelID .. '/group_recursive_search', DumpJson(lTagHandlingList['groupkeep']), false))
        end
        if lTagHandling['groupremovere'] then
            lRecurseGroupRemoveRe = ParseJson(RestApiPost('/series/' .. aoLevelID .. '/group_regexp_recursive_search', DumpJson(lTagHandlingList['groupremovere']), false))
        else
            lRecurseGroupRemoveRe = nil
        end
    end
    -- print('lRecurse Groups')
    -- print(DumpJson(lRecurseProprietary))
    -- print(DumpJson(lRecurseRemove))
    -- if lRecurseGroupKeep then print(DumpJson(lRecurseGroupKeep)) end
    -- if lRecurseGroupRemoveRe then print(DumpJson(lRecurseGroupRemoveRe)) end
    
    local loInstanceID, lGroup, lElement, lField
    for i, loLevelInstanceMeta in pairs(loLevelInstancesMeta) do
        loInstanceID = loLevelInstanceMeta['ID']
        local loInstanceMeta = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/tags', false))
        -- First the UID mapping info
        -- RecursiveFindUIDToKeep(loInstanceMeta)
        local lResult = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/recursive_find_uid_to_keep_lua', false))
        if lResult['status'] and lResult['status'] > 0 then error(lResult['error_text']) end
        for kk,vv in pairs(lResult['TopLevelTagToKeep']) do gTopLevelTagToKeep[kk] = vv end
        for kk,vv in pairs(lResult['KeptUID']) do gKeptUID[kk] = vv end
        for lTagKey, lTagVal in pairs(loInstanceMeta) do
            _, _, lGroup, lElement = string.find(lTagKey, "([^,]+),([^,]+)")
            lField = lGroup .. '-' .. lElement
            lTagsEncountered[lField] = true
        end
        if lTagHandling['groupkeep'] then
            for lTagKey, lTagVal in pairs(loInstanceMeta) do
                _, _, lGroup, lElement = string.find(lTagKey, "([^,]+),([^,]+)")
                if lTagHandling['groupkeep'][lGroup] then
                    lField = lGroup .. '-' .. lElement
                    lTagsToKeep[lField] = true
                end
            end
            for lField, lTagList in pairs(lRecurseGroupKeep) do
                lTagsToKeep[lField] = true
            end
        end
        if lTagHandling['groupremovere'] then
            for lTagKey, lTagVal in pairs(loInstanceMeta) do
                _, _, lGroup, lElement = string.find(lTagKey, "([^,]+),([^,]+)")
                for lGroupRE, lValue in pairs(lTagHandling['groupremovere']) do
                    if string.find(lGroup,lGroupRE) then
                        lField = lGroup .. '-' .. lElement
                        lTagsToRemove[lField] = true
                    end
                end
            end
            if lRecurseGroupRemoveRe then
                for lField, lValueList in pairs(lRecurseGroupRemoveRe) do
                    lTagsToRemove[lField] = true
                end
            end
        end
    end -- loop over instances    
  
    -- Remove any private tags not already explicity kept
    if lTagHandling['KeepSomePrivate'] then
        for i, loLevelInstanceMeta in pairs(loLevelInstancesMeta) do
            loInstanceID = loLevelInstanceMeta['ID']
            local loInstanceMeta = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/tags', false))
            for lTagKey, lTagVal in pairs(loInstanceMeta) do
                _, _, lGroup, lElement = string.find(lTagKey, "([^,]+),([^,]+)")
                if ((tonumber(lGroup,16) % 2) == 1) then
                    local lField = lGroup .. '-' .. lElement
                    if not (lTagHandling['keep'][lField] or lTagsToKeep[lField]) then
                        lTagsToRemove[lField] = true
                    end
                end
            end
        end
        for lField, lProprietary in pairs(lRecurseProprietary) do 
            if not (lTagHandling['keep'][lField] or lTagsToKeep[lField]) then
                lTagsToRemove[lField] = true
            end
        end
    else
        for lField, lProprietary in pairs(lRecurseProprietary) do 
            lTagsToRemove[lField] = true
        end
    end
    -- print('Pre scan results')
    -- print(DumpJson(gTopLevelTagToKeep))
    -- print(DumpJson(gKeptUID))
    -- print(DumpJson(lTagsEncountered))
    -- print(DumpJson(lTagsToKeep))
    -- print(DumpJson(lTagsToRemove))
 
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time so far (1) in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end

    local lDataToPython = {}
    lDataToPython['SQLpid'] = aSQLpid
    if aPatientIDModifier then lDataToPython['PatientIDModifier'] = aPatientIDModifier end
    -- local lSQLInternalNumber = GetInternalNumber(aSQLpid, aPatientIDModifier)
    local lSQLInternalNumberResult = ParseJson(RestApiPost('/get_internal_number_lua', DumpJson(lDataToPython,true), false, {['x-remote-user']='lua-GetInternalNumberLua'}))
    local lSQLInternalNumber
    if lSQLInternalNumberResult['internal_number'] then
        lSQLInternalNumber = lSQLInternalNumberResult['internal_number']
    else
--         gSQLConn:rollback()
--         CloseSQL()
        error(lSQLInternalNumberResult['status']['error_text'])
    end
    -- local ldPatientNameAnon = ConstructPatientName(lSQLInternalNumber)
    local lDataToPython = {}
    lDataToPython['InternalNumber'] = lSQLInternalNumber
    if gPatientNameBase then lDataToPython['PatientNameBase'] = gPatientNameBase end
    if gPatientNameIDChar then lDataToPython['PatientNameIDChar'] = gPatientNameIDChar end
    local ldPatientNameAnon = RestApiPost('/construct_patient_name', DumpJson(lDataToPython,true), false)

    if gVerbose then print(string.rep(' ', gIndent) .. 'Time so far (2) in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end

    -- Tags to be replaced
    local lReplace = {}
    lReplace['PatientName'] = ldPatientNameAnon
    if adPatientIDAnon then
        lReplace['PatientID'] = adPatientIDAnon
    end
    if adStudyInstanceUIDAnon then
        lReplace['StudyInstanceUID'] = adStudyInstanceUIDAnon
    end
    if lTagHandling['empty'] then
        for lField, lValue in pairs(lTagHandling['empty']) do
            lReplace[lField] = ''
        end
    end
    if lTagHandling['emptyseq'] then
        for lField, lValue in pairs(lTagHandling['emptyseq']) do
            lReplace[lField] = {}
        end
    end
    if lTagHandling['emptyx'] then
        for lField, lValue in pairs(lTagHandling['emptyx']) do
            lReplace[lField] = 'xxxxxx'
        end
    end

    local lRemove = {}
    -- Top level tags
    -- for lElement, lValue in pairs(lTagHandling['remove']) do
    --     if lTagsEncountered[lElement] then table.insert(lRemove,lElement) end
    -- end
    -- The above is now accomplised by the python recursive routine.
    for lElement, lValueList in pairs(lRecurseRemove) do
        for i, lValue in pairs(lValueList) do
            table.insert(lRemove, lValue)
        end
    end
    for lElement, lValue in pairs(lTagsToRemove) do
        if not lTagHandling['remove'][lElement] then table.insert(lRemove, lElement) end
        if lRecurseProprietary[lElement] then
            for i, lProprietaryAddress in pairs(lRecurseProprietary[lElement]) do
                table.insert(lRemove, lProprietaryAddress)
            end
        end
        if lTagHandling['groupremovere'] and lRecurseGroupRemoveRe and lRecurseGroupRemoveRe[lElement] then
            for i, lGroupReAddress in pairs(lRecurseGroupRemoveRe[lElement]) do
                table.insert(lRemove, lGroupReAddress)
            end
        end
    end

    local lKeep = {}
    for lElement, lValue in pairs(lTagHandling['keep']) do
        if lTagsEncountered[lElement] then table.insert(lKeep, lElement) end
    end
    for lElement, lValue in pairs(lTagsToKeep) do
        if not lTagHandling['keep'][lElement] then table.insert(lKeep, lElement) end
    end

    lIndex = #lKeep
    for lTagKey, lTagVal in pairs(gTopLevelTagToKeep) do 
        if not string.find(lTagKey,'Unknown') then
            lIndex = lIndex + 1
            lKeep[lIndex] = lTagKey
        end
    end
    -- print('Replace/Remove/Keep')
    -- print(DumpJson(lReplace))
    -- print(DumpJson(lRemove))
    -- print(DumpJson(lKeep))

    -- Modify the study: It seems remove clashes with keep and I need to run them separate
    if gVerbose then print(string.rep(' ', gIndent) .. 'Starting the study modification call') end
    local loStudyIDMod
    local loSeriesIDMod
    local lModifyPostData = {}
    lModifyPostData['Remove'] = lRemove
    local lFlagRemovePrivateTags = os.getenv('LUA_FLAG_REMOVE_PRIVATE_TAGS') == 'true'
    if lFlagRemovePrivateTags and not lTagHandling['KeepSomePrivate'] then
        lModifyPostData['RemovePrivateTags'] = lFlagRemovePrivateTags
    end
    lModifyPostData['Force'] = true
    lModifyPostData['DicomVersion'] = '2008'
    -- print('Modify Post')
    -- print(DumpJson(lModifyPostData))
    if lFlagByStudy then
        local lSuccess, loStudyModMetaJson = pcall(RestApiPost, 
                                                  '/studies/' .. aoLevelID .. '/modify', 
                                                  DumpJson(lModifyPostData,true), false)
        if not lSuccess then
            PrintRecursive(lModifyPostData)
--             gSQLConn:rollback()
--             CloseSQL()
            error('Could not complete modify statement')
        end
        local loStudyModMeta = ParseJson(loStudyModMetaJson)
        loStudyIDMod = loStudyModMeta['ID']
    else
        local lSuccess, loSeriesModMetaJson = pcall(RestApiPost, 
                                                    '/series/' .. aoLevelID .. '/modify', 
                                                    DumpJson(lModifyPostData,true), false)
        if not lSuccess then 
            PrintRecursive(lModifyPostData)
--             gSQLConn:rollback()
--             CloseSQL()
            error('Could no complete modify statement')
        end
        local loSeriesModMeta = ParseJson(loSeriesModMetaJson)
        loSeriesIDMod = loSeriesModMeta['ID']
        loSeriesModMeta = ParseJson(RestApiGet('/series/' .. loSeriesIDMod, false))
        loStudyIDMod = loSeriesModMeta['ParentStudy']
    end
    -- print('StudyIDMod: ' .. loStudyIDMod)
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time so far (3) in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end

    -- Anonymize the study
    if gVerbose then print(string.rep(' ', gIndent) .. 'Starting the study anonymization call') end
    local loStudyIDAnon
    local lAnonPostData = {}
    if lReplace then
        lAnonPostData['Replace'] = lReplace
    end
    lAnonPostData['Keep'] = lKeep
    lAnonPostData['Force'] = true
    lAnonPostData['DicomVersion'] = '2008'
    -- print('AnonPostData')
    -- print(DumpJson(lAnonPostData))
    local loInstancesAnonMeta 
    if lFlagByStudy then
        local lSuccess, loStudyAnonMetaJson = pcall(RestApiPost, 
                                                    '/studies/' .. loStudyIDMod .. '/anonymize', 
                                                    DumpJson(lAnonPostData,true), false)
        if not lSuccess then
            PrintRecursive(lAnonPostData)
--             gSQLConn:rollback()
--             CloseSQL()
            error('Problem calling anonymize')
        end
       
        local loStudyAnonMeta = ParseJson(loStudyAnonMetaJson)
        loStudyIDAnon = loStudyAnonMeta['ID']
        loInstancesAnonMeta = ParseJson(RestApiGet('/studies/' .. loStudyIDAnon .. '/instances', false))
    else
        local lSuccess, loSeriesAnonMetaJson = pcall(RestApiPost,
                                                    '/series/' .. loSeriesIDMod .. '/anonymize', 
                                                     DumpJson(lAnonPostData,true), false)
        if not lSuccess then 
            PrintRecursive(lAnonPostData)
--             gSQLConn:rollback()
--             CloseSQL()
            error('Problem calling anonymize')
        end
        local loSeriesAnonMeta = ParseJson(loSeriesAnonMetaJson)
        local loSeriesIDAnon = loSeriesAnonMeta['ID']
        loSeriesAnonMeta = ParseJson(RestApiGet('/series/' .. loSeriesIDAnon, false))
        loStudyIDAnon = loSeriesAnonMeta['ParentStudy']
        loInstancesAnonMeta = ParseJson(RestApiGet('/series/' .. loSeriesAnonMeta['ID'] .. '/instances', false))
    end
    -- print('InstancesAnonMeta')
    -- print(DumpJson(loInstancesAnonMeta))
    if gVerbose then print(string.rep(' ', gIndent) .. 'N instances anon: ', #loInstancesAnonMeta) end
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time so far (4) in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end

    local loStudyAnonMeta = ParseJson(RestApiGet('/studies/' .. loStudyIDAnon, false))
    -- print('MetaStudyAnon')
    -- print(DumpJson(loStudyAnonMeta))

    if not adPatientIDAnon then
        -- SavePatientIDsAnonToDB(loStudyAnonMeta,aSQLpid)
        local lPostData = {}
        lPostData['OrthancStudyID'] = loStudyAnonMeta['ID']
        lPostData['SQLpid'] = aSQLpid
        -- print('OrthancStudyID: ' .. loStudyAnonMeta['ID'])
        -- print('SQLpid: ' .. aSQLpid)
        local lStatus = ParseJson(RestApiPost('/save_patient_ids_anon_to_db_lua', DumpJson(lPostData), false))
        if lStatus['status'] and lStatus['status'] > 0 then error(lStatus['error_text']) end
    end
    if not adStudyInstanceUIDAnon then
        -- SaveStudyInstanceUIDAnonToDB(loStudyAnonMeta,aSQLsiuid)
        local lPostData = {}
        lPostData['OrthancStudyID'] = loStudyAnonMeta['ID']
        lPostData['SQLsiuid'] = aSQLsiuid
        -- print('OrthancStudyID: ' .. loStudyAnonMeta['ID'])
        -- print('SQLsiuid: ' .. aSQLsiuid)
        local lStatus = ParseJson(RestApiPost('/save_study_instance_uid_anon_to_db_lua', DumpJson(lPostData), false))
        if lStatus['status'] and lStatus['status'] > 0 then error(lStatus['error_text']) end
    end
    local lFlagSavePatientNameAnon = os.getenv('LUA_FLAG_SAVE_PATIENTNAME_ANON') == 'true'
    if lFlagSavePatientNameAnon then
        -- SavePatientNameAnonToDB(ldPatientNameAnon, aSQLsiuid)
        local lPostData = {}
        lPostData['PatientNameAnon'] = ldPatientNameAnon
        lPostData['SQLsiuid'] = aSQLsiuid
        -- print('PatientNameAnon: ' .. ldPatientNameAnon)
        -- print('SQLsiuid: ' .. aSQLsiuid)
        local lStatus = ParseJson(RestApiPost('/save_patient_name_anon_to_db_lua', DumpJson(lPostData), false))
        if lStatus['status'] and lStatus['status'] > 0 then error(lStatus['error_text']) end
    end

    gIndent = gIndent - 3
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
    if gIndent > 0 then gIndent = gIndent - 3 end
    if lFlagSavePatientNameAnon then
        return loInstancesAnonMeta, loStudyIDAnon, ldPatientNameAnon
    else
        return loInstancesAnonMeta, loStudyIDAnon, nil
    end

end

-- -- ======================================================
-- function MapUIDOldToNew(aoStudyIDNew, aFlagRemapSOPInstanceUID, aFlagRemapKeptUID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagRemapSOPInstanceUID = aFlagRemapSOPInstanceUID
--     local lFlagRemapKeptUID = aFlagRemapKeptUID
--     local lUIDMap = {}
--     local lUIDType = {}
-- 
--     -- Cycle through anonymized versions to set up one-to-one maps
--     -- First at the study level
--     local loStudyIDOld, loStudyIDMod
--     local loStudyMetaNew, loStudyMetaOld, loStudyMetaMod
--     local ldStudyInstanceUIDNew, ldStudyInstanceUIDOld, ldStudyInstanceUIDMod
--     loStudyMetaNew = ParseJson(RestApiGet('/studies/' .. aoStudyIDNew, false))
--     ldStudyInstanceUIDNew = loStudyMetaNew['MainDicomTags']['StudyInstanceUID']
-- 
--     loStudyIDMod = loStudyMetaNew['AnonymizedFrom']
--     loStudyMetaMod = ParseJson(RestApiGet('/studies/' .. loStudyIDMod, false))
--     ldStudyInstanceUIDMod = loStudyMetaMod['MainDicomTags']['StudyInstanceUID']
-- 
--     loStudyIDOld = loStudyMetaMod['ModifiedFrom']
--     loStudyMetaOld = ParseJson(RestApiGet('/studies/' .. loStudyIDOld, false))
--     ldStudyInstanceUIDOld = loStudyMetaOld['MainDicomTags']['StudyInstanceUID']
--     lUIDMap[ldStudyInstanceUIDOld] = ldStudyInstanceUIDNew
--     lUIDType[ldStudyInstanceUIDOld] = 'StudyInstanceUID'
-- 
--     local loSeriesIDOld, loSeiesIDMod
--     local loSeriesMetaNew, loSeriesMetaOld, loSeriesMetaMod
--     local ldSeriesInstanceUIDNew, ldSeriesInstanceUIDOld, ldSeriesInstanceUIDMod
-- 
--     local loInstanceIDOld
--     local loInstanceMetaNew, loInstanceMetaOld, loInstanceMetaMod
--     local ldSOPInstanceUIDNew, ldSOPInstanceUIDOld, ldSOPInstanceUIDMod
-- 
--     for i, loSeriesIDNew in pairs(loStudyMetaNew['Series']) do
-- 
--         -- Now series
--         loSeriesMetaNew = ParseJson(RestApiGet('/series/' .. loSeriesIDNew, false))
--         ldSeriesInstanceUIDNew = loSeriesMetaNew['MainDicomTags']['SeriesInstanceUID']
-- 
--         loSeriesIDMod = loSeriesMetaNew['AnonymizedFrom']
--         loSeriesMetaMod = ParseJson(RestApiGet('/series/' .. loSeriesIDMod, false))
--         if not loSeriesMetaMod then
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Missing series:' .. loSeriesIDMod .. ' of ' .. aoStudyIDNew ) end
--         end
--         ldSeriesInstanceUIDMod = loSeriesMetaMod['MainDicomTags']['SeriesInstanceUID']
-- 
--         loSeriesIDOld = loSeriesMetaMod['ModifiedFrom']
--         loSeriesMetaOld = ParseJson(RestApiGet('/series/' .. loSeriesIDOld, false))
--         ldSeriesInstanceUIDOld = loSeriesMetaOld['MainDicomTags']['SeriesInstanceUID']
-- 
--         lUIDMap[ldSeriesInstanceUIDOld] = ldSeriesInstanceUIDNew
--         lUIDType[ldSeriesInstanceUIDOld] = 'SeriesInstanceUID'
-- 
--         for j, loInstanceIDNew in pairs(loSeriesMetaNew['Instances']) do
--             -- Now instances 
--             loInstanceMetaNew = ParseJson(RestApiGet('/instances/' .. loInstanceIDNew, false))
--             ldSOPInstanceUIDNew = loInstanceMetaNew['MainDicomTags']['SOPInstanceUID']
--             loInstanceIDMod = loInstanceMetaNew['AnonymizedFrom'] 
--             loInstanceMetaMod = ParseJson(RestApiGet('/instances/' .. loInstanceIDMod, false))
--             ldSOPInstanceUIDMod = loInstanceMetaMod['MainDicomTags']['SOPInstanceUID']
--             loInstanceIDOld = loInstanceMetaMod['ModifiedFrom'] 
--             if loInstanceIDOld then 
--                 loInstanceMetaOld = ParseJson(RestApiGet('/instances/' .. loInstanceIDOld, false))
--                 ldSOPInstanceUIDOld = loInstanceMetaOld['MainDicomTags']['SOPInstanceUID']
--                 lUIDMap[ldSOPInstanceUIDOld] = ldSOPInstanceUIDNew
--                 lUIDType[ldSOPInstanceUIDOld] = 'SOPInstanceUID'
--                 -- Delete the Modified intermediate
--                 RestApiDelete('/instances/' .. loInstanceIDMod, false)
--             end
-- 
--             if lFlagRemapSOPInstanceUID then
--                 local ldInstanceUIDRemap = RestApiGet('/tools/generate-uid?level=instance') 
--                 lUIDMap[ldSOPInstanceUIDNew] = ldInstanceUIDRemap
--                 lUIDType[ldSOPInstanceUIDNew] = 'SOPInstanceUID'
--             end
-- 
--         end
-- 
--     end
-- 
--     -- Now check for non-modified UID
--     if lFlagRemapKeptUID then
--         for lKeptUIDVal, lKeptUIDType in pairs(gKeptUID) do
-- 
--             -- We really only care if it does not exist
--             if not lUIDMap[lKeptUIDVal] then
-- 
--                 if string.find(lKeptUIDType['Name'], 'StudyInstanceUID') or string.find(lKeptUIDType['Name'], 'FrameOfReferenceUID') then
--                     ldStudyInstanceUIDNew = RestApiGet('/tools/generate-uid?level=study') 
--                     lUIDMap[lKeptUIDVal] =  ldStudyInstanceUIDNew
--                     lUIDType[lKeptUIDVal] = lKeptUIDType['Name']
--                 end
-- 
--                 if string.find(lKeptUIDType['Name'], 'SeriesInstanceUID') then
--                     ldSeriesInstanceUIDNew = RestApiGet('/tools/generate-uid?level=series') 
--                     lUIDMap[lKeptUIDVal] =  ldSeriesInstanceUIDNew
--                     lUIDType[lKeptUIDVal] = lKeptUIDType['Name']
--                 end
-- 
--                 if string.find(lKeptUIDType['Name'], 'SOPInstanceUID') then
--                     local ldInstanceUIDRemap
--                     ldInstanceUIDRemap = RestApiGet('/tools/generate-uid?level=instance') 
--                     lUIDMap[lKeptUIDVal] = ldInstanceUIDRemap
--                     lUIDType[lKeptUIDVal] = lKeptUIDType['Name']
--                 end
-- 
--                 if string.find(lKeptUIDType['Name'], 'SOPClassUID') or string.find(lKeptUIDType['Name'], 'CodingScheme') then -- we keep these
--                     lUIDMap[lKeptUIDVal] = lKeptUIDVal
--                     lUIDType[lKeptUIDVal] = lKeptUIDType['Name']
--                 end
-- 
--                 -- Generic catch all will be a study uid
--                 if not lUIDMap[lKeptUIDVal] then
--                     ldStudyInstanceUIDNew = RestApiGet('/tools/generate-uid?level=study') 
--                     lUIDMap[lKeptUIDVal] =  ldStudyInstanceUIDNew
--                     lUIDType[lKeptUIDVal] = lKeptUIDType['Name']
--                 end
-- 
--             end
-- 
--         end
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lUIDMap, lUIDType
-- 
-- end
-- 
-- -- ======================================================
-- function LoadShiftEpochFromDB(aSQLpid)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lSQLQuery = string.format([[SELECT value FROM shiftepoch WHERE pid=%d]],aSQLpid)
--     local lSQLStatus, lSQLCursor
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem selecting shiftepoch")
--     end
--     if lSQLCursor:numrows() > 0 then
--         local lSQLRow = lSQLCursor:fetch({}, "a")
--         gIndent = gIndent - 3
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--         if gIndent > 0 then gIndent = gIndent - 3 end
--         return lSQLRow.value
--     end
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- -- ======================================================
-- function SaveShiftEpochToDB(aShiftEpoch,aSQLpid)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to false') end
--     local lSQLResult = gSQLConn:setautocommit(false)
--     local lSQLQuery = string.format(
--                         [[INSERT INTO shiftepoch (value,pid) VALUES(%d,%d)]],
--                         aShiftEpoch, aSQLpid)
--     local lSQLStatus, lSQLResult = pcall(gSQLConn.execute,gSQLConn, lSQLQuery)
--     if not lSQLStatus then
--         lSQLResult = gSQLConn:rollback()
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--         lSQLResult = gSQLConn:setautocommit(true)
--         CloseSQL()
--         error("Problem inserting shiftepoch")
--     end
--     lSQLResult = gSQLConn:commit()
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Setting autocommit to true') end
--     lSQLResult = gSQLConn:setautocommit(true)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- -- ======================================================
-- function ComputeShiftEpochFromEarliestDate(aoInstancesMeta)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lDicomFields = { 'Study', 'Series', 'Acquisition', 
--                            'Content', 'InstanceCreation',
--                            'PerformedProcedureStepStart' }
--     local lDateTimeFields = { 'AcquisitionDateTime' }
--     -- Default to current time if no date/time fields found
--     local lMinEpoch = os.time()
--     local lDateField, lTimeField
--     for i, loInstanceMeta in pairs(aoInstancesMeta) do
--         local loInstanceID = (loInstanceMeta['ID'])
--         local lSuccess, loDicomTagsJson =pcall(RestApiGet,
--                                                '/instances/' .. loInstanceID .. '/simplified-tags',
--                                                 false)
--         if not lSuccess then
--             gSQLConn:rollback()
--             CloseSQL()
--             error('Could not query instance for tags')
--         end
--         local loDicomTags = ParseJson(loDicomTagsJson)
--         -- local loDicomTags = 
--         --        ParseJson(RestApiGet('/instances/' .. 
--         --                             loInstanceID .. '/simplified-tags', false))
--         for j, lDicomField in pairs(lDicomFields) do
--             local lDateField = lDicomField .. 'Date'
--             local lTimeField = lDicomField .. 'Time'
--             if loDicomTags[lDateField] and string.len(trim(loDicomTags[lDateField])) > 0 then
--                 if loDicomTags[lTimeField] and string.len(trim(loDicomTags[lTimeField])) > 0 then
--                     local lYear           = tonumber(string.sub(loDicomTags[lDateField],1,4))
--                     local lMonth          = tonumber(string.sub(loDicomTags[lDateField],5,6))
--                     local lDay            = tonumber(string.sub(loDicomTags[lDateField],7,8))
--                     local lHour           = tonumber(string.sub(loDicomTags[lTimeField],1,2))
--                     local lMinute         = tonumber(string.sub(loDicomTags[lTimeField],3,4))
--                     local lSec = math.floor(tonumber(string.sub(loDicomTags[lTimeField],5)) or 0)
--                     if not lMinEpoch then
--                         lMinEpoch = os.time{year=lYear, 
--                                            month=lMonth or 1, 
--                                            day=lDay or 1, 
--                                            hour=lHour or 0, 
--                                            min=lMinute or 0, 
--                                            sec=lSec or 0}
--                     else
--                         lMinEpoch = math.min(lMinEpoch, os.time{year=lYear, 
--                                                               month=lMonth or 1, 
--                                                               day=lDay or 1, 
--                                                               hour=lHour or 0, 
--                                                               min=lMinute or 0, 
--                                                               sec=lSec or 0 })
--                     end
--                 else
--                     if gVerbose then 
--                         print ('No matching time for date: ' .. lDateField .. ', ' .. lTimeField)
--                         PrintRecursive(loDicomTags)
--                     end
--                 end
--             end -- endif found lDateField
--         end -- loop over lDicomFields
--         for j, lDateTimeField in pairs(lDateTimeFields) do 
--             if loDicomTags[lDateTimeField] and string.len(trim(loDicomTags[lDateTimeField])) > 0 then
--                 local lYear           = tonumber(string.sub(loDicomTags[lDateTimeField],1,4))
--                 local lMonth          = tonumber(string.sub(loDicomTags[lDateTimeField],5,6))
--                 local lDay            = tonumber(string.sub(loDicomTags[lDateTimeField],7,8))
--                 local lHour           = tonumber(string.sub(loDicomTags[lDateTimeField],9,10))
--                 local lMinute         = tonumber(string.sub(loDicomTags[lDateTimeField],11,12))
--                 local lSec = math.floor(tonumber(string.sub(loDicomTags[lDateTimeField],13)) or 0)
--                 if not lMinEpoch then
--                     lMinEpoch = os.time{year=lYear, 
--                                        month=lMonth or 1, 
--                                        day=lDay or 1, 
--                                        hour=lHour or 0, 
--                                        min=lMinute or 0, 
--                                        sec=lSec or 0}
--                 else
--                     lMinEpoch = math.min(lMinEpoch, 
--                                         os.time{year=lYear, 
--                                                 month=lMonth or 1, 
--                                                 day=lDay or 1, 
--                                                 hour=lHour or 0, 
--                                                 min=lMinute or 0, 
--                                                 sec=lSec or 0 })
--                 end
--             end
--         end -- loop over lDateTimeFields
--     end -- loop over aoInstancesMeta
--     local lTemp = os.date("*t", lMinEpoch)
--     local lMinYear = lTemp['year']
--     local lShiftEpoch = lMinEpoch - os.time{year=lMinYear, 
--                                             month=1, 
--                                             day=1, 
--                                             hour=12, 
--                                             min=0, 
--                                             sec=0}
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lShiftEpoch
-- 
-- end
-- 
-- -- ======================================================
-- function RecursiveReplaceUID(aParent, aLevelIn)
-- 
--     gMaxRecurseDepth = 20
--     local lElement
--     local lLevelIn = (aLevelIn) or gMaxRecurseDepth
--     local lLevelOut = lLevelIn - 1
--     if not aLevelIn then
--         gAddressConstructor = {}
--         gAddressList = {}
--     end
--     if (lLevelIn<1) then return {}, lLevelOut end;
--     local lParentType = type(aParent);
--     lElement = {}
--     if (lParentType ~= "table") then return lElement, lLevelOut end
--     local lUIDNew
--     local lValue
--     if aParent['Value'] then
--         if type(aParent['Value']) == "table" then
--             for k,lChild in pairs(aParent['Value']) do  
--                 table.insert(gAddressConstructor, aParent['Name'] .. "[" .. tostring(k-1) .. "]")
--                 lValue, iLevelOut = RecursiveReplaceUID(lChild, lLevelIn-1)
--                 if (lLevelOut < 0) then break end
--                 if type(lValue) == "table" then
--                     if next(lValue) then lElement[k] = lValue end
--                 else
--                     if string.len(lValue) > 0 then lElement[k] = lValue end
--                 end
--                 table.remove(gAddressConstructor)
--             end
--         else
--             if string.find(aParent['Name'],'UID') then
--                 table.insert(gAddressConstructor, aParent['Name'])
--                 lUIDNew = aParent['Value']
--                 while gUIDMap[lUIDNew] do
--                     if lUIDNew == gUIDMap[lUIDNew] then break end
--                     lUIDNew = gUIDMap[lUIDNew]
--                 end
--                 local lAddressEntry = ""
--                 local lNAddressStub = #gAddressConstructor
--                 for k, lAddressStub in pairs(gAddressConstructor) do
--                     if (k < lNAddressStub) then
--                         lAddressEntry = lAddressEntry .. lAddressStub .. "."
--                     else
--                         lAddressEntry = lAddressEntry .. lAddressStub
--                     end
--                 end
--                 gAddressList[lAddressEntry] = lUIDNew
--                 aParent['Value'] = lUIDNew
--                 table.remove(gAddressConstructor)
--             end
--             return aParent['Value'], iLevelOut
--         end
--     else
--         for k,lChild in pairs(aParent) do  
--             lValue, iLevelOut = RecursiveReplaceUID(lChild, lLevelIn-1)
--             if (lLevelOut < 0) then break end
--             if type(lValue) == "table" then
--                 if next(lValue) then lElement[k] = lValue end
--             else
--                 if string.len(lValue) > 0 then lElement[k] = lValue end
--             end
--         end
--     end
--     return lElement, iLevelOut
-- 
-- end
-- 
-- -- -- ======================================================
-- function ShiftDateTimeString(aShiftEpoch,aYYYYMMDDString,aHHMMSSString)
--    
--     local lYear = tonumber(string.sub(aYYYYMMDDString, 1, 4))
--     local lMonth = tonumber(string.sub(aYYYYMMDDString,5,6))
--     local lDay = tonumber(string.sub(aYYYYMMDDString,7,8))
-- 
--     local lHour, lMinute, lSec, lSecFrac
--     local lHHMMSSString 
--     if aHHMMSSString then
--         if string.len(trim(aHHMMSSString)) >= 6 then
--            lHHMMSSString = aHHMMSSString
--         else
--            if gVerbose then print(string.rep(' ', gIndent+3) .. 'Bad shift date time string ' .. aHHMMSSString) end
--            lHHMMSSString = nil
--         end
--     end
--     if lHHMMSSString then
--         lHour = tonumber(string.sub(lHHMMSSString, 1, 2))
--         lMinute = tonumber(string.sub(lHHMMSSString,3,4))
--         local lSecString = string.sub(lHHMMSSString,5)
--         lSec = math.floor(tonumber(lSecString) or 0)
--         if string.find(lSecString,'%.') then
--             lSecFrac = string.sub(lSecString,3)
--         else
--             lSecFrac = nil
--         end
--     elseif string.len(aYYYYMMDDString) > 12 then
--         lHour = tonumber(string.sub(aYYYYMMDDString, 9, 10))
--         lMinute = tonumber(string.sub(aYYYYMMDDString,11,12))
--         local lSecString 
--         if string.find(aYYYYMMDDString, '%-') then
--             lSecString = string.sub(aYYYYMMDDString,13,14)
--         else
--             lSecString = string.sub(aYYYYMMDDString,13)
--         end
--         lSec = math.floor(tonumber(lSecString))
--         if string.find(lSecString,'%.') then
--             lSecFrac = string.sub(lSecString,3)
--         else
--             lSecFrac = nil
--         end
--     else
--         lHour = 0
--         lMinute = 0
--         lSec = 0
--     end
--     local lThisEpoch = os.time{year=lYear, 
--                                month=lMonth or 1, 
--                                day=lDay or 1, 
--                                hour=lHour or 0, 
--                                min=lMinute or 0, 
--                                sec=lSec or 0}
--     local lTemp = os.date("*t", lThisEpoch)
--     local lThisDST = lTemp['isdst']
-- 
--     local lNewEpoch = lThisEpoch - aShiftEpoch
--     local lTemp = os.date("*t", lNewEpoch)
--     local lNewDST = lTemp['isdst']
-- 
--     -- Preserve the original hour, minute, second
--     local lNewHour = lHour
-- 
--     local lNewDateString
--     if string.len(aYYYYMMDDString) > 12 then
--         if lSecFrac then
--             lNewDateString = 
--                 string.format("%04d%02d%02d%02d%02d%0d%s", 
--                               lTemp['year'], lTemp['month'], 
--                               lTemp['day'], lNewHour, 
--                               lTemp['min'], lTemp['sec'], lSecFrac)
--         else
--             lNewDateString = 
--                 string.format("%04d%02d%02d%02d%02d%02d.0", 
--                               lTemp['year'], lTemp['month'], 
--                               lTemp['day'], lNewHour, 
--                               lTemp['min'], lTemp['sec'])
--         end
--     else
--         lNewDateString = string.format("%04d%02d%02d", lTemp['year'], lTemp['month'], lTemp['day'])
--     end
--     local lNewTimeString = nil
--     if aHHMMSSString then
--         if lSecFrac then
--            lNewTimeString = string.format("%02d%02d%02d%s", lNewHour, lTemp['min'], lTemp['sec'], lSecFrac)
--         else
--            lNewTimeString = string.format("%02d%02d%02d.0", lNewHour, lTemp['min'], lTemp['sec'])
--         end
--     end
-- 
--     return lNewDateString, lNewtimeString
-- 
-- end
--    
-- -- ======================================================
-- function ShiftDateTimePatAgeOfInstances(aoInstancesMeta, aShiftEpoch, aReplaceRoot)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lDicomFields = { 'Study', 'Series', 'Acquisition', 
--                            'Content', 'InstanceCreation',
--                            'PerformedProcedureStepStart' }
--     local lDateTimeFields = { 'AcquisitionDateTime' }
--     local lDateTimeFieldsRadio = { 'RadiopharmaceuticalStartDateTime', 'RadiopharmaceuticalStopDateTime' }
--     local loInstanceIDNew = {}
--     local lNumInstances = 0
--     for i, loInstanceMeta in pairs(aoInstancesMeta) do lNumInstances = lNumInstances+1 end
--     local lTenPercent = math.ceil(lNumInstances / 10)
--     local lPostData = {}
--     lPostData['orthanc_instance_ids'] = {}
--     for i, loInstanceMeta in pairs(aoInstancesMeta) do
--         table.insert(lPostData['orthanc_instance_ids'], loInstanceMeta['ID'])
--     end
--     local lResults = ParseJson(RestApiPost('/send_instances_to_remote_filter_lua', DumpJson(lPostData), false))
--     if not lResults then
--        error('Problem calling send_instances_to_remote_filter_lua')
--     end 
--     -- for i, loInstanceMeta in pairs(aoInstancesMeta) do
--     local i = 0
--     for loInstanceID, lFlagSendToRemote in pairs(lResults) do
--         i = i + 1
--         if gVerbose and (((i-1) % lTenPercent) == 0) then print(string.rep(' ', gIndent) .. 'Progress', i, 'of', lNumInstances) end
--         local lReplace = {}
--         for lReplaceRootKey, lReplaceRootVal in pairs(aReplaceRoot) do
--             lReplace[lReplaceRootKey] = lReplaceRootVal
--         end
--         -- local loInstanceID = (loInstanceMeta['ID'])
--         -- local lFlagSendToRemote = SendToRemoteFilter(loInstanceID)
--         local loDicomTags
--         if lFlagSendToRemote then
--             loDicomTags = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/simplified-tags', false))
--         else
--             loDicomTags = {}
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Shift date will skip non orig/prim /instances/' .. loInstanceID .. '/simplified-tags') end
--         end
--         for j, lDicomField in pairs(lDicomFields) do
--             local lDateField = lDicomField .. 'Date'
--             local lTimeField = lDicomField .. 'Time'
--             if loDicomTags[lDateField] and string.len(trim(loDicomTags[lDateField])) > 0 then
--                 if loDicomTags[lTimeField] and string.len(trim(loDicomTags[lTimeField])) > 0 then
--                     -- local lNewDateString, lNewTimeString
--                     -- lNewDateString, lNewTimeString = 
--                     --     ShiftDateTimeString(aShiftEpoch, loDicomTags[lDateField], loDicomTags[lTimeField])
--                     local lPostData = {}
--                     lPostData['ShiftEpoch'] = aShiftEpoch
--                     lPostData['YYYYMMDD'] = loDicomTags[lDateField]
--                     lPostData['HHMMSS'] = loDicomTags[lTimeField]
--                     local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--                     lReplace[lDateField] = lResults['NewDateString']
--                     lReplace[lTimeField] = lResults['NewTimeString']
--                 else
--                     if gVerbose then 
--                         print ('No matching time for date: ' .. lDateField .. ', ' .. lTimeField)
--                         -- PrintRecursive(loDicomTags)
--                     end
--                 end
--             end
--         end -- loop over lDicomFields
--         for j, lDateTimeField in pairs(lDateTimeFields) do 
--             if loDicomTags[lDateTimeField] and string.len(trim(loDicomTags[lDateTimeField])) > 0 then
--                 -- lReplace[lDateTimeField] = ShiftDateTimeString(aShiftEpoch, loDicomTags[lDateTimeField])
--                 local lPostData = {}
--                 lPostData['ShiftEpoch'] = aShiftEpoch
--                 lPostData['YYYYMMDD'] = loDicomTags[lDateTimeField]
--                 local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--                 lReplace[lDateTimeField] = lResults['NewDateString']
--                 -- lReplace[lDateTimeField] = ShiftDateTimeString(aShiftEpoch, loDicomTags[lDateTimeField])
--             end
--         end -- loop over lDateTimeFields
--         local lRadio = 'RadiopharmaceuticalInformationSequence'
--         if loDicomTags[lRadio] then
--             lReplace[lRadio] = loDicomTags[lRadio]
--             for lItem, lTags in pairs(loDicomTags[lRadio]) do
--                 for j, lDateTimeField in pairs(lDateTimeFieldsRadio) do 
--                     if lTags[lDateTimeField] and string.len(trim(lTags[lDateTimeField])) > 0 then
--                         -- lReplace[lRadio][lItem][lDateTimeField] = ShiftDateTimeString(aShiftEpoch, lTags[lDateTimeField])
--                         local lPostData = {}
--                         lPostData['ShiftEpoch'] = aShiftEpoch
--                         lPostData['YYYYMMDD'] = lTags[lDateTimeField]
--                         local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--                         lReplace[lRadio][lItem][lDateTimeField] = lResults['NewDateString']
--                     end
--                 end -- loop over lDateTimeFields
--             end
--         end
-- 
--         if loDicomTags['PatientBirthDate'] then
--             -- lReplace['PatientBirthDate'] = ShiftDateTimeString(aShiftEpoch, loDicomTags['PatientBirthDate'])
--             local lPostData = {}
--             lPostData['ShiftEpoch'] = aShiftEpoch
--             lPostData['YYYYMMDD'] = loDicomTags['PatientBirthDate']
--             local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--             lReplace['PatientBirthDate'] = lResults['NewDateString']
--         end
--         if loDicomTags['PatientAge'] then
--             local lAgeNumber = tonumber(string.sub(loDicomTags['PatientAge'], 1, 3))
--             local lAgeUnit = string.sub(loDicomTags['PatientAge'],4)
--             if lAgeUnit == 'Y' then
--                 if lAgeNumber > 89 then
--                     lAgeNumber = 90
--                     lReplace['PatientAge'] = string.format("%03dY", lAgeNumber)
--                 end
--             end
--         end
--         if loDicomTags['SOPInstanceUID'] then
--             local ldSOPInstanceUIDNew = gUIDMap[loDicomTags['SOPInstanceUID']]
--             while gUIDMap[ldSOPInstanceUIDNew] do
--                 ldSOPInstanceUIDNew = gUIDMap[ldSOPInstanceUIDNew]
--             end
--             lReplace['SOPInstanceUID'] = ldSOPInstanceUIDNew
--         end
--         if lFlagSendToRemote then
--             loDicomTags = ParseJson(RestApiGet('/instances/' .. loInstanceID .. '/tags', false))
--             local lPostData = {}
--             lPostData['UIDMap'] = gUIDMap
--             for lTagKey, lTagVal in pairs(gTopLevelTagToKeep) do 
--                 if loDicomTags[lTagKey] then
--                     --if type(loDicomTags[lTagKey]) == 'table' then
--                     if type(loDicomTags[lTagKey]['Value']) == 'table' then
--                         local iReplaceValue, lLevelOut
--                         -- iReplaceValue, lLevelOut = RecursiveReplaceUID(loDicomTags[lTagKey])
--                         lPostData['Parent'] = loDicomTags[lTagKey]
--                         local lResults = ParseJson(RestApiPost('/recursive_replace_uid_lua', DumpJson(lPostData), false))
--                         iReplaceValue = lResults['ReplaceValue']
--                         lLevelOut = lResults['LevelOut']
--                         gAddressList = lResults['AddressList']
--                         if gAddressList then
--                             for lAddressKey, lAddressVal in pairs(gAddressList) do
--                                 lReplace[lAddressKey] = lAddressVal
--                             end
--                         end
--                         --lReplace[lTagKey] = iReplaceValue
--                     else
--                         local lUIDNew = gUIDMap[loDicomTags[lTagKey]['Value']]
--                         while gUIDMap[lUIDNew] do
--                             if lUIDNew == gUIDMap[lUIDNew] then break end
--                             lUIDNew = gUIDMap[lUIDNew]
--                         end
--                         lReplace[lTagKey] = lUIDNew
--                     end
--                 end
--             end
--         end
-- 
--         if next(loDicomTags) then
--             local lPostData = {}
--             lPostData['Replace'] = lReplace
--             -- lPostData['DicomVersion'] = '2017c'
--             -- lPostData['DicomVersion'] = '2008'
--             lPostData['Force'] = true
--             lPostDataJson = DumpJson(lPostData,true)
--             local lSuccess, lModifiedDICOMBlob = pcall(RestApiPost,
--                                                        '/instances/' .. loInstanceID .. '/modify', 
--                                                        lPostDataJson, false)
--             if not lSuccess then
--                 PrintRecursive(lPostDataJson)
-- --                 gSQLConn:rollback()
-- --                 CloseSQL()
--                 error('Unable to adjust dates')
--             end
--             -- Upload the lModifiedDICOMBlob
--             local lSuccess, loModifiedInstanceIDJson = pcall(RestApiPost,
--                                                              '/instances/', lModifiedDICOMBlob, false)
--             if not lSuccess then
-- --                 gSQLConn:rollback()
-- --                 CloseSQL()
--                 error('Problem uploading new image blob')
--             end
--             --local loModifiedInstanceID = ParseJson(RestApiPost('/instances/', lModifiedDICOMBlob, false))['ID']
--             local loModifiedInstanceID = ParseJson(loModifiedInstanceIDJson)['ID']
--             -- Store new ID
--             loInstanceIDNew[i] = loModifiedInstanceID
--         end
--     
--     end -- loop over aoInstancesMeta
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if (gIndent > 0) then gIndent = gIndent - 3 end
--     return loInstanceIDNew
-- 
-- end
--  
-- -- ======================================================
-- function SendToRemoteFilter(aoInstanceID)
-- 
--     local loDicomTags = ParseJson(RestApiGet('/instances/' .. aoInstanceID .. '/simplified-tags', false))
--     -- By default we assume derived (for safety) unless proven otherwise by existing ImageType 
--     local lFlagAssumeOriginalPrimary = os.getenv('LUA_FLAG_ASSUME_ORIGINAL_PRIMARY') == 'true'
-- 
--     local lFlagOriginalPrimary = lFlagAssumeOriginalPrimary
--     local lFlagPrimary = lFlagAssumeOriginalPrimary
--     local lCharStartOriginal, lCharStopOriginal, lCharStartPrimary, lCharStopPrimary
--     if not lFlagAssumeOriginalPrimary then -- Turn off in order to keep Derived/Secondaries
--         if loDicomTags['ImageType'] then
--             lCharStartOriginal, lCharStopOriginal = string.find(loDicomTags['ImageType'],'ORIGINAL')
--             lCharStartPrimary, lCharStopPrimary = string.find(loDicomTags['ImageType'],'PRIMARY')
--             lFlagOriginalPrimary = (lCharStartOriginal == 1) and (lCharStartPrimary == (lCharStopOriginal + 2))
--             lFlagPrimary = lFlagPrimary or lCharStartPrimary
--         else
--             if loDicomTags['FrameType'] then
--                 lCharStartOriginal, lCharStopOriginal = string.find(loDicomTags['FrameType'],'ORIGINAL')
--                 lCharStartPrimary, lCharStopPrimary = string.find(loDicomTags['FrameType'],'PRIMARY')
--                 lFlagPrimary = lFlagPrimary or lCharStartPrimary
--                 lFlagOriginalPrimary = (lCharStartOriginal == 1) and (lCharStartPrimary == (lCharStopOriginal + 2))
--             end
--         end
--     end
-- 
--     -- Exception for HIFU and Dynacad
--     local lFlagDynacad = false
--     -- lFlagDynacad = lFlagDynacad or string.find(loDicomTags['SeriesDescription'], 'DCAD-')
--     -- lFlagDynacad = lFlagDynacad or (loDicomTags['0073,1003'] and string.find(loDicomTags['0073,1003'],'DYNACAD'))
--     
--     -- Checking for non-mammo images
--     local lFlagScreenForReports = os.getenv('LUA_FLAG_SCREEN_FOR_REPORTS') == 'true' -- turn on to weed out reports
--     local lFlagNonReport
--     if loDicomTags['ImageType'] then
--         lFlagNonReport = true
--     else
--         lFlagNonReport = false
--     end
--     if lFlagScreenForReports then -- Test for unwanted mammo studies
--         if lFlagNonReport and loDicomTags['ImageType'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['ImageType']), 'dose'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['ImageType']), 'screen'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['ImageType']), 'report'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['ImageType']), 'exam protocol'))
--         end
--         if lFlagNonReport and loDicomTags['StudyDescription'] then
--             -- lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['StudyDescription']), 'no rpt'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['StudyDescription'], 'SecurView'))
--         end
--         if lFlagNonReport and loDicomTags['SecondaryCaptureDeviceManufacturer'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SecondaryCaptureDeviceManufacturer'], 'PACSGEAR'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SecondaryCaptureDeviceManufacturer'], 'HipGrahics'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SecondaryCaptureDeviceManufacturer'], 'Lexmark'))
--         end
--         if lFlagNonReport and loDicomTags['SecondaryCaptureDeviceManufacturerModelName'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SecondaryCaptureDeviceManufacturerModelName'], 'PACSSCAN'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SecondaryCaptureDeviceManufacturerModelName'], 'InSpace'))
--         end
--         if lFlagNonReport and loDicomTags['StationName'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['StationName']), 'rapid'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['StationName']), 'sonosite'))
--         end
--         if lFlagNonReport and loDicomTags['Manufacturer'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['Manufacturer']), 'ischemaview'))
--         end
--         if lFlagNonReport and loDicomTags['ManufacturerModelName'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['ManufacturerModelName'], 'SecurView'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['ManufacturerModelName'], 'Blackford'))
--         end
--         if lFlagNonReport and loDicomTags['SeriesDescription'] then
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['SeriesDescription']), 'screen snapshot'))
--             lFlagNonReport = lFlagNonReport and (not string.match(string.lower(loDicomTags['SeriesDescription']), 'screen *s[a-z]*er*'))
--             lFlagNonReport = lFlagNonReport and (not string.match(string.lower(loDicomTags['SeriesDescription']), '*dose report*'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['SeriesDescription']), 'no rpt'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['SeriesDescription']), 'summary'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['SeriesDescription']), 'vpct'))
--             lFlagNonReport = lFlagNonReport and (not string.find(string.lower(loDicomTags['SeriesDescription']), 'history'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'RAPID'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'SecurView'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'Patient Protocol'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'Phoenix'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'Carestream'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'REQ'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'REPORT'))
--             lFlagNonReport = lFlagNonReport and (not string.find(loDicomTags['SeriesDescription'], 'Blackford'))
--         end
--     end
--     -- Consider both original and primary
--     if (os.getenv('LUA_FLAG_MUST_BE_ORIGINAL') == 'true') then 
--        return lFlagDynacad or (lFlagOriginalPrimary and lFlagNonReport)
--     -- else only primary
--     else
--        return lFlagDynacad or (lFlagPrimary and lFlagNonReport)
--     end
-- 
-- end
--  
-- -- ======================================================
-- function PreScreenSendToRemote(aoStudyID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagDeleted = false
--     
--     local loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
--     local lNSeriesStart = #loStudyMeta['Series']
-- 
--     local lPostData = {}
--     lPostData['orthanc_study_ids'] = { aoStudyID } 
--     local lResults = ParseJson(RestApiPost('/send_instances_to_remote_filter_lua', DumpJson(lPostData), false))
--     if not lResults then
--        error('Problem calling send_instances_to_remote_filter_lua')
--     end 
--     for loInstanceID, lFlagSendToRemote in pairs(lResults) do
--         if not lFlagSendToRemote then
--             if gVerbose then print(string.rep(' ', gIndent) .. 'Prefilter will delete non orig/prim /instances/' .. loInstanceID .. '/simplified-tags') end
--             RestApiDelete('/instances/' .. loInstanceID, false)
--         end
--     end
--     
--     -- for i, loSeriesID in pairs(loStudyMeta['Series']) do
--     --     local loSeriesMeta = ParseJson(RestApiGet('/series/' .. loSeriesID, false))
--     --     if loSeriesMeta['MainDicomTags'] then 
--     --         if loSeriesMeta['Instances'] then
--     --             for ioInstanceID, oInstanceID in pairs(loSeriesMeta['Instances']) do
--     --                 local lFlagSendToRemote = SendToRemoteFilter(oInstanceID)
--     --                 if not lFlagSendToRemote then
--     --                     if gVerbose then print(string.rep(' ', gIndent) .. 'Prefilter will delete non orig/prim /instances/' .. oInstanceID .. '/simplified-tags') end
--     --                     RestApiDelete('/instances/' .. oInstanceID, false)
--     --                 end
--     --             end
--     --         end
--     --     end
--     -- end
-- 
--     loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
--     local lNSeriesEnd = 0
--     if loStudyMeta then
--         if loStudyMeta['Series'] then
--             lNSeriesEnd = #loStudyMeta['Series']
--         end
--     end
--     local lNSeriesDeleted = lNSeriesStart - lNSeriesEnd
--     if lNSeriesStart > lNSeriesEnd then lFlagDeleted = true end
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lFlagDeleted, lNSeriesStart, lNSeriesDeleted
-- 
-- end
-- 
-- -- ======================================================
-- function PreScreenSeriesByModality(aoStudyID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagDeleted = false
--     local lAllowedModalities = {}
--     if string.len(trim(os.getenv('LUA_ALLOWED_MODALITIES'))) > 0 then
--         for lModality in string.gmatch(os.getenv('LUA_ALLOWED_MODALITIES'), '[^," ]+') do
--             if lModality and string.len(trim(lModality)) > 0 then
--                 table.insert(lAllowedModalities,lModality)
--             end
--         end
--     end
--     local lDeniedModalities = {}
--     if string.len(trim(os.getenv('LUA_DENIED_MODALITIES'))) > 0 then
--         for lModality in string.gmatch(os.getenv('LUA_DENIED_MODALITIES'), '[^," ]+') do
--             if lModality and string.len(trim(lModality)) > 0 then
--                 table.insert(lDeniedModalities, lModality)
--             end
--         end
--     end
--     local lFlagAllowed 
--     local loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
--     local lNSeriesStart = #loStudyMeta['Series']
--     local lNSeriesDeleted = 0
--     for i, loSeriesID in pairs(loStudyMeta['Series']) do
--         local loSeriesMeta = ParseJson(RestApiGet('/series/' .. loSeriesID, false))
--         if loSeriesMeta['MainDicomTags'] then 
--              if loSeriesMeta['MainDicomTags']['Modality'] then
--                  lFlagAllowed = #lAllowedModalities == 0
--                  for j, lAllowedModality in pairs(lAllowedModalities) do
--                      lFlagAllowed = lFlagAllowed or (loSeriesMeta['MainDicomTags']['Modality'] == lAllowedModality)
--                  end
--                  for j, lDeniedModality in pairs(lDeniedModalities) do
--                      lFlagAllowed = lFlagAllowed and (loSeriesMeta['MainDicomTags']['Modality'] ~= lDeniedModality)
--                  end
--                  if not lFlagAllowed then
--                      if gVerbose then print(string.rep(' ', gIndent) .. 'Deleting non modality series', loSeriesID) end
--                      RestApiDelete('/series/' .. loSeriesID, false)
--                      lFlagDeleted = true
--                      lNSeriesDeleted = lNSeriesDeleted + 1
--                  end
--              end
--          end
--     end
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lFlagDeleted, lNSeriesStart, lNSeriesDeleted
-- 
-- end
-- 
-- -- ======================================================
-- function CheckSplit2DFromCViewTomo(aoStudyID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local loSeriesMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID .. '/series', false))
-- 
--     -- We need R/L CC, R/L MLO for 2D and C-View (others are extra)
--     local lSearchStrings = { 'r cc', 'l cc', 'r mlo', 'l mlo' }
--     local lCount2D = {0, 0, 0, 0}
--     local lCountCView = {0, 0, 0, 0}
--     for i, loSeriesData in pairs(loSeriesMeta) do
--         local lFlagCView = false
--         local lFlagNon2D = false
--         if loSeriesData['MainDicomTags']['SeriesDescription'] then
--             local lDescriptionLower = string.lower(loSeriesData['MainDicomTags']['SeriesDescription'])
--             lFlagCView = lFlagCView or string.find(lDescriptionLower, 'c-view')
--             lFlagNon2D = lFlagNon2D or lFlagCView
--             lFlagNon2D = lFlagNon2D or string.find(lDescriptionLower, 'tomo')
--             if lFlagCView or (not lFlagNon2D) then
--                 for j = 1, 4 do 
--                     local lFoundStr = string.find(lDescriptionLower, lSearchStrings[j])
--                     if lFoundStr then
--                         if lFlagCView then
--                             lCountCView[j] = 1
--                         else
--                             lCount2D[j] = 1
--                         end
--                     end
--                 end
--             end
--         end
--     end -- Initial loop over all series descriptions
--     local lSum2D = 0
--     local lSumCView = 0
--     for i = 1, 4 do 
--         lSum2D = lSum2D + lCount2D[i]
--         lSumCView = lSumCView + lCountCView[i]
--     end
-- 
--     if (lSum2D < 4) or (lSumCView < 4) then
--         print('Incomplete number of either 2D or C-View')
--         PrintRecursive(lCount2D)
--         PrintRecursive(lCountCView)
--         gIndent = gIndent - 3
--         print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0)
--         if gIndent > 0 then gIndent = gIndent - 3 end
--         return false
--     else
--         gIndent = gIndent - 3
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--         if gIndent > 0 then gIndent = gIndent - 3 end
--         return true
--     end
-- 
-- end
-- 
-- ======================================================
function AnonymizeStudyBySeries(aoStudyID, aoStudyMeta)

    if gIndent then gIndent=gIndent+3 else gIndent=0 end
    if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
    gIndent = gIndent + 3
    local lTime0 = os.time()
    -- Assume we've already pre-screened for modality

    -- Get the Orthanc series ID associated with this study
    local lPatientIDModifierBySeries = {}
    local lSQLpidBySeries = {}
    local ldPatientIDAnonBySeries = {}
    local lSQLsiuidBySeries = {}
    local ldStudyInstanceUIDAnonBySeries = {}
    local lFlagNewPatientIDBySeries = {}
    local lFlagNewStudyInstanceUIDBySeries = {}
    for i, loSeriesID in pairs(aoStudyMeta['Series']) do

--         if gSQLOpen then
--             if gSQLConn then
--                 CloseSQL()
--             end
--         end
--         gSQLOpen = false
--         OpenSQL()

        -- Get series meta
        local loSeriesMeta = ParseJson(RestApiGet('/series/' .. loSeriesID, false))

        -- We modify the incoming patientIDs based on descriptions
        -- Currently, we modify by 2D vs non-2D
        local lPatientIDModifier = ''
        local lFlagSplit2DFromCViewTomo = os.getenv('LUA_FLAG_SPLIT_2D_FROM_CVIEW_TOMO') == 'true'
        if lFlagSplit2DFromCViewTomo then 
            -- lPatientIDModifier = Set2DOrCViewTomo(loSeriesMeta)
            lPatientIDModifier = RestApiGet('/series/' .. loSeriesID .. '/set_2d_or_cview_tomo_lua', false)
        end
        local lFlagEveryAccessionAPatient = os.getenv('LUA_FLAG_EVERY_ACCESSION_A_PATIENT') == 'true'
        if lFlagEveryAccessionAPatient then lPatientIDModifier = '_' .. aoStudyMeta['MainDicomTags']['AccessionNumber'] end
        lPatientIDModifierBySeries[loSeriesID] = lPatientIDModifier

        -- Check to see if this subject was previously anonymized
        -- StudyInstanceUID is only modified when anonymizing at the series level
        local lStudyInstanceUIDModifier = lPatientIDModifier
        local lSQLpid, ldPatientIDAnon, lSQLsiuid, ldStudyInstanceUIDAnon
        --local lFlagNewPatientID, lSQLpid, ldPatientIDAnon = SavePatientIDsToDB(aoStudyMeta,lPatientIDModifier)
        local lPostData = {}
        lPostData['OrthancStudyID'] = aoStudyMeta['ID']
        if lPatientIDModifier then lPostData['PatientIDModifier'] = lPatientIDModifier end
        local lResults
        lResults = ParseJson(RestApiPost('/save_patient_ids_to_db_lua', DumpJson(lPostData), false))
        if lResults['status'] and lResults['status'] > 0 then
--             gSQLConn:rollback()
--             CloseSQL()
            error(lResults['error_text'])
        end
        local lFlagNewPatientID = lResults['FlagPatientNewID']
        -- local lSQLpid = math.floor(lResults['SQLpid']+0.5)
        local lSQLpid = lResults['SQLpid']
        local ldPatientIDAnon = lResults['PatientIDAnon']
        -- local lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon = SaveStudyInstanceUIDToDB(aoStudyMeta,lSQLpid,lStudyInstanceUIDModifier)
        local lPostData = {}
        lPostData['OrthancStudyID'] = aoStudyMeta['ID']
        lPostData['SQLpid'] = lSQLpid
        if lStudyInstanceUIDModifier then lPostData['StudyInstanceUIDModifier'] = lStudyInstanceUIDModifier end
        local lResults
        lResults = ParseJson(RestApiPost('/save_study_instance_uid_to_db_lua', DumpJson(lPostData), false))
        if lResults['status'] then error(lResults['error_text']) end
        local lFlagNewStudyInstanceUID = lResults['FlagNewStudyInstanceUID']
        local lSQLsiuid = lResults['SQLsiuid']
        local ldStudyInstanceUIDAnon = lResults['StudyInstanceUIDAnon']
        
        lFlagNewPatientIDBySeries[loSeriesID] = lFlagNewPatientID
        lSQLpidBySeries[loSeriesID] = lSQLpid
        ldPatientIDAnonBySeries[loSeriesID] = ldPatientIDAnon
        lFlagNewStudyInstanceUIDBySeries[loSeriesID] = lFlagNewStudyInstanceUID
        lSQLsiuidBySeries[loSeriesID] = lSQLsiuid
        ldStudyInstanceUIDAnonBySeries[loSeriesID] = ldStudyInstanceUIDAnon

--        CloseSQL()
        
    end -- First loop over series to get modifiers and series specific IDs

    -- Compute unique set of identifiers
    local lPatientIDModifierUnique = {}
    local lFlagNewPatientID = {}
    local lFlagNewStudyInstanceUID = {}
    local lSQLpid = {}
    local ldPatientIDAnon = {}
    local lSQLsiuid = {}
    local ldStudyInstanceUIDAnon = {}
    for loSeriesID,lPatientIDModifier in pairs(lPatientIDModifierBySeries) do
        if not lPatientIDModifierUnique[lPatientIDModifier] then
            lPatientIDModifierUnique[lPatientIDModifier] = {loSeriesID}
            lFlagNewPatientID[lPatientIDModifier] = lFlagNewPatientIDBySeries[loSeriesID]
            lFlagNewStudyInstanceUID[lPatientIDModifier] = lFlagNewStudyInstanceUIDBySeries[loSeriesID]
            lSQLpid[lPatientIDModifier] = lSQLpidBySeries[loSeriesID]
            ldPatientIDAnon[lPatientIDModifier] = ldPatientIDAnonBySeries[loSeriesID]
            lSQLsiuid[lPatientIDModifier] = lSQLsiuidBySeries[loSeriesID]
            ldStudyInstanceUIDAnon[lPatientIDModifier] = ldStudyInstanceUIDAnonBySeries[loSeriesID]
        else
            table.insert(lPatientIDModifierUnique[lPatientIDModifier], loSeriesID)
            lFlagNewPatientID[lPatientIDModifier] = lFlagNewPatientID[lPatientIDModifier] or lFlagNewPatientIDBySeries[loSeriesID]
            lFlagNewStudyInstanceUID[lPatientIDModifier] = lFlagNewStudyInstanceUID[lPatientIDModifier] or lFlagNewStudyInstanceUIDBySeries[loSeriesID]
            if lSQLpid[lPatientIDModifier] ~= lSQLpidBySeries[loSeriesID] then
                error("Mismatch in SQLpid assigned to series with same patient modifier")
            end
            if ldPatientIDAnon[lPatientIDModifier] ~= ldPatientIDAnonBySeries[loSeriesID] then
                error("Mismatch in dPatientIDAnon assigned to series with same patient modifier")
            end
            if lSQLsiuid[lPatientIDModifier] ~= lSQLsiuidBySeries[loSeriesID] then
                error("Mismatch in SQLsiuid assigned to series with same patient modifier")
            end
            if ldStudyInstanceUIDAnon[lPatientIDModifier] ~= ldStudyInstanceUIDAnonBySeries[loSeriesID] then
                error("Mismatch in dStudyInstanceUIDAnon assigned to series with same patient modifier")
            end
        end
    end

    -- Now loop over sets of series by their modifier
    local lFlagImagesSent = false
    for lPatientIDModifier, loSeriesIDs in pairs(lPatientIDModifierUnique) do

--         if gSQLOpen then
--             if gSQLConn then
--                 CloseSQL()
--             end
--         end
--         gSQLOpen = false
--         OpenSQL()

        -- We're not going to bother anonymizing unless either a new patient or study
        local lFlagNonOriginalDetected = false
        local lFlagForceAnon = false or gFlagForceAnon
        local ldPatientNameAnonDict = {}
        if lFlagForceAnon or (lFlagNewPatientID[lPatientIDModifier] or lFlagNewStudyInstanceUID[lPatientIDModifier]) then

            -- First pass anonymization
            local loInstancesAnonMeta, loStudyIDAnon
            local lFlagFirstCall = true
            for i, loSeriesID in ipairs(loSeriesIDs) do 
                local loInstancesAnonMetaTemp, loStudyIDAnonTemp , ldPatientNameAnonTemp
                -- loInstancesAnonMetaTemp, loStudyIDAnonTemp, ldPatientNameAnonTemp = 
                --    AnonymizeInstances('Series', loSeriesID, lFlagFirstCall, 
                --                        lSQLpid[lPatientIDModifier],ldPatientIDAnon[lPatientIDModifier],
                --                        lSQLsiuid[lPatientIDModifier], ldStudyInstanceUIDAnon[lPatientIDModifier], 
                --                        lPatientIDModifier)
                local lPostData = {}
                if gAddressConstructor then lPostData['AddressConstructor'] = gAddressConstructor end
                if gAddressList then lPostData['AddressList'] = gAddressList end
                lPostData['Level'] = 'Series'
                lPostData['LevelID'] =loSeriesID 
                lPostData['FlagFirstCall'] = lFlagFirstCall
                if gKeptUID then lPostData['KeptUID'] = gKeptUID end
                if ldPatientIDAnon[lPatientIDModifier] then lPostData['PatientIDAnon'] = ldPatientIDAnon[lPatientIDModifier] end
                if lPatientIDModifier then lPostData['PatientIDModifier'] = lPatientIDModifier end
                if gPatientNameBase then lPostData['PatientNameBase'] = gPatientNameBase end
                if gPatientNameIDChar then lPostData['PatientNameIDChar'] = gPatientNameIDChar end
                lPostData['SQLpid'] = lSQLpid[lPatientIDModifier]
                lPostData['SQLsiuid'] = lSQLsiuid[lPatientIDModifier]
                if ldStudyInstanceUIDAnon[lPatientIDModifier] then lPostData['StudyInstanceUIDAnon'] = ldStudyInstanceUIDAnon[lPatientIDModifier] end
                if gTopLevelTagToKeep then lPostData['TopLevelTagToKeep'] = gTopLevelTagToKeep end
                if gUIDMap then lPostData['UIDMap'] = gUIDMap end
                local lResult = ParseJson(RestApiPost('/anonymize_instances_lua', DumpJson(lPostData,false)))
                if lResult['status'] then error('Problem with anonymization ' .. lResult['error_text']) end
                if lResult['AddressConstructor'] then gAddressConstructor  = lResult['AddressConstructor'] end
                if lResult['AddressList'] then gAddressList  = lResult['AddressList'] end
                loInstancesAnonMetaTemp = lResult['InstancesAnonMeta']
                if lResult['KeptUID'] then gKeptUID  = lResult['KeptUID'] end
                if lResult['PatientNameAnon'] then ldPatientNameAnonTemp = lResult['PatientNameAnon'] end
                if lResult['PatientNameBase'] then gPatientNameBase  = lResult['PatientNameBase'] end
                if lResult['PatientNameIDChar'] then gPatientNameIDChar  = lResult['PatientNameIDChar'] end
                loStudyIDAnonTemp = lResult['StudyIDAnon']
                if lResult['TopLevelTagToKeep'] then gTopLevelTagToKeep  = lResult['TopLevelTagToKeep'] end
                if lResult['UIDMap'] then gUIDMap = lResult['UIDMap'] end
                if ldPatientNameAnonTemp then ldPatientNameAnonDict[ldPatientNameAnonTemp] = true end
                if lFlagFirstCall then
                    loInstancesAnonMeta = loInstancesAnonMetaTemp
                    loStudyIDAnon = loStudyIDAnonTemp
                    -- We call "Save" again just to read in the newly saved IDs (they were saved inside the anonymize routine)
                    local lStudyInstanceUIDModifier = lPatientIDModifier
                    local lSQLpidTemp, ldPatientIDAnonTemp, lSQLsiuidTemp, ldStudyInstanceUIDAnonTemp
                    -- local lFlagNewPatientIDTemp, lSQLpidTemp, ldPatientIDAnonTemp = SavePatientIDsToDB(aoStudyMeta,lPatientIDModifier)
                    local lPostData = {}
                    lPostData['OrthancStudyID'] = aoStudyMeta['ID']
                    if lPatientIDModifier then lPostData['PatientIDModifier'] = lPatientIDModifier end
                    local lResults
                    lResults = ParseJson(RestApiPost('/save_patient_ids_to_db_lua', DumpJson(lPostData), false))
                    if lResults['status'] and  lResults['status'] > 0 then
--                         gSQLConn:rollback()
--                         CloseSQL()
                        error(lResults['error_text'])
                    end
                    local lFlagNewPatientIDTemp = lResults['FlagPatientNewID']
                    local lSQLpidTemp = lResults['SQLpid']
                    local ldPatientIDAnonTemp = lResults['PatientIDAnon']
                    if lSQLpid[lPatientIDModifier] ~= lSQLpidTemp then
                        error('Unexpected mismatch when reading SQLpid')
                    end
                    if not ldPatientIDAnon[lPatientIDModifier] then
                        ldPatientIDAnon[lPatientIDModifier] = ldPatientIDAnonTemp
                    else
                        if lFlagNewPatientIDTemp or (ldPatientIDAnon[lPatientIDModifier] ~= ldPatientIDAnonTemp) then
                            error('Unexpected mismatch when reading dPatientIDAnon')
                        end
                    end
                    -- local lFlagNewStudyInstanceUIDTemp, lSQLsiuidTemp, ldStudyInstanceUIDAnonTemp = SaveStudyInstanceUIDToDB(aoStudyMeta,lSQLpidTemp,lStudyInstanceUIDModifier)
                    local lPostData = {}
                    lPostData['OrthancStudyID'] = aoStudyMeta['ID']
                    lPostData['SQLpid'] = lSQLpidTemp
                    if lStudyInstanceUIDModifier then lPostData['StudyInstanceUIDModifier'] = lStudyInstanceUIDModifier end
                    local lResults
                    lResults = ParseJson(RestApiPost('/save_study_instance_uid_to_db_lua', DumpJson(lPostData), false))
                    if lResults['status'] then error(lResults['error_text']) end
                    local lFlagNewStudyInstanceUIDTemp = lResults['FlagNewStudyInstanceUID']
                    local lSQLsiuidTemp = lResults['SQLsiuid']
                    local ldStudyInstanceUIDAnonTemp = lResults['StudyInstanceUIDAnon']
                    if lSQLsiuid[lPatientIDModifier] ~= lSQLsiuidTemp then
                        error('Unexpected mismatch when reading SQLsiuid')
                    end
                    if not ldStudyInstanceUIDAnon[lPatientIDModifier] then
                        ldStudyInstanceUIDAnon[lPatientIDModifier] = ldStudyInstanceUIDAnonTemp
                    else
                        if lFlagNewStudyInstanceUIDTemp or (ldStudyInstanceUIDAnon[lPatientIDModifier] ~= ldStudyInstanceUIDAnonTemp) then
                            error('Unexpected mismatch when reading dStudyInstanceUIDAnon')
                        end
                    end
                else
                    -- Add instances to list of instances already anonymized
                    for j=1,#loInstancesAnonMetaTemp do
                        loInstancesAnonMeta[#loInstancesAnonMeta+1] = loInstancesAnonMetaTemp[j]
                    end
                    -- StudyIDAnon should not have changed
                    if loStudyIDAnon ~= loStudyIDAnonTemp then
                        error("Unexpected change in IDAnon for same modifier")
                    end
                end
                lFlagFirstCall = false
            end -- loop over series belonging to the current modifier

            -- Set up old-->new UID map
            local lFlagRemapSOPInstanceUID = true
            local lFlagRemapKeptUID = true
            -- gUIDMap, gUIDType = MapUIDOldToNew(loStudyIDAnon,lFlagRemapSOPInstanceUID,lFlagRemapKeptUID)
            local lPostData = {}
            lPostData['StudyIDNew'] = loStudyIDAnon
            lPostData['FlagRemapSOPInstanceUID'] = lFlagRemapSOPInstanceUID
            lPostData['FlagRemapKeptUID'] = lFlagRemapKeptUID
            lPostData['KeptUID'] = gKeptUID
            local lResults = ParseJson(RestApiPost('/map_uid_old_to_new_lua', DumpJson(lPostData), false))
            gUIDMap = lResults['UIDMap']
            gUIDType = lResults['UIDType']

            -- Set up replacements for AccessionNumber and StudyID
            local lReplaceRoot = {}
            lReplaceRoot['AccessionNumber'] = string.sub(loStudyIDAnon,1,8) .. string.sub(loStudyIDAnon,10,17)
            lReplaceRoot['StudyID'] = string.sub(loStudyIDAnon,19,26) .. string.sub(loStudyIDAnon,28,35)
    
            -- Check for existing lShiftEpoch
            -- local lShiftEpoch = LoadShiftEpochFromDB(lSQLpid[lPatientIDModifier])
            local lPostData = {}
            lPostData['SQLpid'] = lSQLpid[lPatientIDModifier]
            local lStatus = ParseJson(RestApiPost('/load_shift_epoch_from_db_lua', DumpJson(lPostData), false))
            if lStatus['status'] and lStatus['status'] > 0 then error(lStatus['error_text']) end
            local lShiftEpoch = lStatus['ShiftEpoch']

            -- ------------------------------------------------
            -- Compute lShiftEpoch
            local lSaveShiftEpoch = false
            if not lShiftEpoch then 
                -- Compute lShiftEpoch (used to shift earliest date to Jan 01 same year)
                -- lShiftEpoch = ComputeShiftEpochFromEarliestDate(loInstancesAnonMeta)
                -- Compute random shift up to one year
                math.randomseed(os.time())
                lShiftEpoch = math.floor(math.floor(math.random() * 365.0) * 24.0 * 3600.0)
                lSaveShiftEpoch = true
            end

            -- For some cases, we keep the dates, so lShiftEpoch=0
            local lFlagKeepOriginalDates = os.getenv('LUA_FLAG_KEEP_ORIGINAL_DATES') == 'true'
            if lFlagKeepOriginalDates then
                local currentTime = os.time
                lShiftEpoch = 0
            end

            if lSaveShiftEpoch then
                -- SaveShiftEpochToDB(lShiftEpoch,lSQLpid[lPatientIDModifier])
                local lPostData = {}
                lPostData['SQLpid'] = lSQLpid[lPatientIDModifier]
                lPostData['ShiftEpoch'] = lShiftEpoch
                local lStatus = ParseJson(RestApiPost('/save_shift_epoch_to_db_lua', DumpJson(lPostData), false))
                if lStatus['status'] and lStatus['status'] > 0 then
                    error('Problem saving ShiftEpoch to DB')
                end
            end

            -- ------------------------------------------------
            -- Second pass anonymization creates files modified by lShiftEpoch
            -- Deletes First pass anonymized files following lShiftEpoch modification
            local lPostData = {}
            lPostData['InstancesMeta'] = loInstancesAnonMeta
            lPostData['ShiftEpoch'] = lShiftEpoch
            lPostData['ReplaceRoot'] = lReplaceRoot
            lPostData['UIDMap'] = gUIDMap
            lPostData['TopLevelTagToKeep'] = gTopLevelTagToKeep
            lPostData['AddressList'] = gAddressList
            lPostData['KeptUID'] = gKeptUID
            -- local loInstanceIDNew = ShiftDateTimePatAgeOfInstances(loInstancesAnonMeta, lShiftEpoch, lReplaceRoot)
            local lResults = ParseJson(RestApiPost('/shift_date_time_patage_of_instances_lua', DumpJson(lPostData), false))
            if lResults['status'] ~= 0 then
                error('Problem calling python shift date time patage')
            end
            loInstanceIDNew = lResults['InstanceIDNew']

            -- Delete the original instance
            for i, loInstanceAnonMeta in pairs(loInstancesAnonMeta) do
                loInstanceID = (loInstanceAnonMeta['ID'])
                RestApiDelete('/instances/' .. loInstanceID, false)
                --Delete(loInstanceID)
            end -- loop over loInstancesAnonMeta
    
            -- Send to receiving modality
            local lPostData = {}
            lPostData['orthanc_instance_ids'] = {}
            for i, loInstanceID in pairs(loInstanceIDNew) do
                table.insert(lPostData['orthanc_instance_ids'], loInstanceID)
            end
            local lResults = ParseJson(RestApiPost('/send_instances_to_remote_filter_lua', DumpJson(lPostData), false))
            if not lResults then
               error('Problem calling send_instances_to_remote_filter_lua')
            end 
            -- for i, loInstanceID in pairs(loInstanceIDNew) do
            for loInstanceID, lFlagSendToRemote in pairs(lResults) do
                -- local lFlagSendToRemote = SendToRemoteFilter(loInstanceID)
                if lFlagSendToRemote then
                    local dumby=3
                    if not lFlagForceAnon then
                        -- RestApiPost('/modalities/' .. os.getenv('LUA_ANON_ORTHANC') .. '/store', loInstanceID, false)
                        lFlagImagesSent = true
                    end
                else
                    RestApiDelete('/instances/' .. loInstanceID, false)
                    lFlagNonOriginalDetected = true
                end
            end

        else -- existing patient/study combo

           if gVerbose then print(string.rep(' ',gIndent) .. 'Skipping re-anon of existing patient/study') end

        end -- endif new patient or new study

        if lFlagNonOriginalDetected then
            if gVerbose then print('Some non-original images were not sent') end
        end

--        CloseSQL()
        
    end -- loop over sets of Orthanc series with the same modifier

    if lFlagImagesSent and gVerbose then
        print(string.rep(' ',gIndent) .. 'Images sent to remote modalities') 
    end
    
    -- UpdateLookupHTML()
    if gVerbose then print(string.rep(' ',gIndent) .. 'Updating lookup table') end
    RestApiGet('/update_lookup_table_html_lua', false)
    local ldPatientNameAnon = '.'
    if next(ldPatientNameAnonDict) then
        ldPatientNameAnon = ':'
        for ldPatientNameAnonTemp, _ in pairs(ldPatientNameAnonDict) do
            if ldPatientNameAnon == ':' then
                ldPatientNameAnon = ldPatientNameAnon .. ' ' .. ldPatientNameAnonTemp
            else
                ldPatientNameAnon = ldPatientNameAnon .. ', ' .. ldPatientNameAnonTemp
            end
        end
    end
    SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Anon Complete', 'Anonymization complete ' .. ldPatientNameAnon)

    gIndent = gIndent - 3
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
    if gIndent > 0 then gIndent = gIndent - 3 end

end

-- ======================================================
function OnStableStudyMain(aoStudyID, aTags, aoStudyMeta)

    if gIndent then gIndent=gIndent+3 else gIndent=0 end
    if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
    gIndent = gIndent - 3
    if gVerbose then print(string.rep(' ', gIndent) .. 'Anonymizing ' .. aoStudyID) end
    if gVerbose and gFlagForceAnon then print(string.rep(' ', gIndent) .. 'Forcing anonymization') end
    local lTime0 = os.time()
    local loSystemMeta = ParseJson(RestApiGet('/system', false))
    local loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
    if (not loStudyMeta) then
        if gVerbose then print('No meta in response') end
        return
    end
    if string.find(loStudyMeta['PatientMainDicomTags']['PatientName'], loSystemMeta['Name']) then 
        if gVerbose then print('Appears to be already anonymized (name match)') end
        return
    end

    local lFlagImagesSent = false
    if (not loStudyMeta['ModifiedFrom']) and (not loStudyMeta['AnonymizedFrom']) and (not loStudyMeta['ModifiedFrom']) then

        -- Check that previously anonymized studies are not on Orthanc
        if not gFlagForceAnon then
            for lIOtherStudyID, loOtherStudyID in pairs(ParseJson(RestApiGet('/studies', false))) do
                local loOtherStudyMeta = ParseJson(RestApiGet('/studies/' .. loOtherStudyID, false))
                if (loOtherStudyMeta['AnonymizedFrom'] == aoStudyID) or (loOtherStudyMeta['ModifiedFrom'] == aoStudyID) then
                   if gVerbose then print('already anonymized') end
                   gIndent = gIndent - 3
                   if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
                   if gIndent > 0 then gIndent = gIndent - 3 end
                   return
                end 
            end
        end

        -- Filter by original/primary and other status
        local lFlagPreScreenSendToRemote = os.getenv('LUA_FLAG_PRESCREEN_ORIGINAL_PRIMARY') == 'true'
        if lFlagPreScreenSendToRemote then
            local lFlagDeleted, lNSeriesStart, lNSeriesDeleted
            -- lFlagDeleted, lNSeriesStart, lNSeriesDeleted = PreScreenSendToRemote(aoStudyID) 
            lResults = ParseJson(RestApiPost('/prescreen_send_to_remote_lua', DumpJson(aoStudyID), false))
            lFlagDeleted = lResults['FlagDeleted']
            lNSeriesStart = lResults['NSeriesStart']
            lNSeriesDeleted = lResults['NSeriesDeleted']
            if lFlagDeleted then
                loStudyMeta = nil
                for lIOtherStudyID, loOtherStudyID in pairs(ParseJson(RestApiGet('/studies', false))) do
                    if (loOtherStudyID == aoStudyID) then
                        loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
                    end
                end
            end
            if not loStudyMeta then
                gIndent = gIndent - 3
                if gVerbose then 
                    print(string.rep(' ', gIndent) .. 'All series deleted by prefilter. Aborting anonymization.')
                    print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0)
                end
                if gIndent > 0 then gIndent = gIndent - 3 end
                return
            end
        end

        -- Filter by modality
        local lFlagPreScreenByModality = os.getenv('LUA_FLAG_PRESCREEN_BY_MODALITY') == 'true'
        if lFlagPreScreenByModality then
            local lFlagDeleted, lNSeriesStart, lNSeriesDeleted
            -- lFlagDeleted, lNSeriesStart, lNSeriesDeleted = PreScreenSeriesByModality(aoStudyID) 
            lResults = ParseJson(RestApiPost('/prescreen_send_to_remote_lua', DumpJson(aoStudyID), false))
            lFlagDeleted = lResults['FlagDeleted']
            lNSeriesStart = lResults['NSeriesStart']
            lNSeriesDeleted = lResults['NSeriesDeleted']
            if lFlagDeleted then
                loStudyMeta = nil
                for lIOtherStudyID, loOtherStudyID in pairs(ParseJson(RestApiGet('/studies', false))) do
                    if (loOtherStudyID == aoStudyID) then
                        loStudyMeta = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
                    end
                end
            end
            if not loStudyMeta then
                gIndent = gIndent - 3
                if gVerbose then 
                    print(string.rep(' ', gIndent) .. 'All series deleted by modality. Aborting anonymization.')
                    print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0)
                end
                if gIndent > 0 then gIndent = gIndent - 3 end
                return
            end
        end

        local lFlagAnonymizeBySeries = os.getenv('LUA_FLAG_ANON_BY_SERIES') == 'true'
        if lFlagAnonymizeBySeries then
            local lFlagSplit2DFromCViewTomo = os.getenv('LUA_FLAG_SPLIT_2D_FROM_CVIEW_TOMO') == 'true'
            if lFlagSplit2DFromCViewTomo then
                -- local lFlagComplete = CheckSplit2DFromCViewTomo(aoStudyID)
                lFlagComplete = ParseJson(RestApiPost('/check_split_2d_from_cview_tomo_lua', DumpJson(aoStudyID), false))
                if not lFlagComplete then return end
            end
            AnonymizeStudyBySeries(aoStudyID, loStudyMeta)
            gIndent = gIndent - 3
            if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
            if gIndent > 0 then gIndent = gIndent - 3 end
            return
        end

--         if gSQLOpen then
--             if gSQLConn then
--                 CloseSQL()
--             end
--         end
--         gSQLOpen = false
--         OpenSQL()

        -- We modify the incoming patientIDs based on descriptions
        -- If "screen" appears in the description, the modifier is 's' else 'd' for diagnostic
        -- This has the effect of generating possibly to anonymous subjects for each incoming subject
        -- Comment out the call to the routine if you want normal use of PatientIDs
        local lPatientIDModifier = ''
        local lFlagSplitScreenFromDiagnostic = os.getenv('LUA_FLAG_SPLIT_SCREEN_DIAG') == 'true'
        -- if lFlagSplitScreenFromDiagnostic then lPatientIDModifier = SetScreenOrDiagnostic(aoStudyID) end
        if lFlagSplitScreenFromDiagnostic then lPatientIDModifier = RestApiGet('/studies/' .. aoStudyID .. '/set_screen_or_diagnostic', false) end
        local lFlagEveryAccessionAPatient = os.getenv('LUA_FLAG_EVERY_ACCESSION_A_PATIENT') == 'true'
        if lFlagEveryAccessionAPatient then lPatientIDModifier = '_' .. loStudyMeta['MainDicomTags']['AccessionNumber'] end

        -- Check to see if this subject was previously anonymized
        -- StudyInstanceUID is only modified when anonymizing at the series level
        local lStudyInstanceUIDModifier = ''
        local lSQLpid, ldPatientIDAnon, lSQLsiuid, ldStudyInstanceUIDAnon
        -- local lFlagNewPatientID, lSQLpid, ldPatientIDAnon = SavePatientIDsToDB(loStudyMeta,lPatientIDModifier)
        local lPostData = {}
        lPostData['OrthancStudyID'] = loStudyMeta['ID']
        if lPatientIDModifier then lPostData['PatientIDModifier'] = lPatientIDModifier end
        local lResults
        lResults = ParseJson(RestApiPost('/save_patient_ids_to_db_lua', DumpJson(lPostData), false))
        if lResults['status'] and lResults['status'] > 0 then
--             gSQLConn:rollback()
--             CloseSQL()
            error(lResults['error_text'])
        end
        local lFlagNewPatientID = lResults['FlagPatientNewID']
        local lSQLpid = lResults['SQLpid']
        local ldPatientIDAnon = lResults['PatientIDAnon']
        -- local lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon = SaveStudyInstanceUIDToDB(loStudyMeta,lSQLpid,lStudyInstanceUIDModifier)
        local lPostData = {}
        lPostData['OrthancStudyID'] = loStudyMeta['ID']
        lPostData['SQLpid'] = lSQLpid
        if lStudyInstanceUIDModifier then lPostData['StudyInstanceUIDModifier'] = lStudyInstanceUIDModifier end
        local lResults
        lResults = ParseJson(RestApiPost('/save_study_instance_uid_to_db_lua', DumpJson(lPostData), false))
        if lResults['status'] then error(lResults['error_text']) end
        local lFlagNewStudyInstanceUID = lResults['FlagNewStudyInstanceUID']
        local lSQLsiuid = lResults['SQLsiuid']
        local ldStudyInstanceUIDAnon = lResults['StudyInstanceUIDAnon']

        -- We're not going to bother anonymizing unless either a new patient or study
        local lFlagNonOriginalDetected = false
        local lFlagForceAnon = false or gFlagForceAnon
        if lFlagForceAnon or (lFlagNewPatientID or lFlagNewStudyInstanceUID) then

            -- First pass anonymization
            local loInstancesAnonMeta, loStudyIDAnon, ldPatientNameAnon
            local lFlagFirstCall = true
            if false then
                loInstancesAnonMeta, loStudyIDAnon, ldPatientNameAnon = AnonymizeInstances('Study', aoStudyID, lFlagFirstCall, 
                                                                                           lSQLpid,ldPatientIDAnon,
                                                                                           lSQLsiuid,ldStudyInstanceUIDAnon, lPatientIDModifier)
            else
                local lPostData = {}
                if gAddressConstructor then lPostData['AddressConstructor'] = gAddressConstructor end
                if gAddressList then lPostData['AddressList'] = gAddressList end
                lPostData['FlagFirstCall'] = lFlagFirstCall
                if gKeptUID then lPostData['KeptUID'] = gKeptUID end
                lPostData['Level'] = 'Study'
                lPostData['LevelID'] = aoStudyID
                if ldPatientIDAnon then lPostData['PatientIDAnon'] = ldPatientIDAnon end
                if lPatientIDModifier then lPostData['PatientIDModifier'] = lPatientIDModifier end
                if gPatientNameBase then lPostData['PatientNameBase'] = gPatientNameBase end
                if gPatientNameIDChar then lPostData['PatientNameIDChar'] = gPatientNameIDChar end
                lPostData['SQLpid'] = lSQLpid
                lPostData['SQLsiuid'] = lSQLsiuid
                if ldStudyInstanceUIDAnon then lPostData['StudyInstanceUIDAnon'] = ldStudyInstanceUIDAnon end
                if gTopLevelTagToKeep then lPostData['TopLevelTagToKeep'] = gTopLevelTagToKeep end
                if gUIDMap then lPostData['UIDMap'] = gUIDMap end
                local lResult = ParseJson(RestApiPost('/anonymize_instances_lua', DumpJson(lPostData,false)))
                if lResult['status'] then error('Problem with anonymization ' .. lResult['error_text']) end
                if lResult['AddressConstructor'] then gAddressConstructor = lResult['AddressConstructor'] end
                if lResult['AddressList'] then gAddressList  = lResult['AddressList'] end
                loInstancesAnonMeta = lResult['InstancesAnonMeta']
                if lResult['KeptUID'] then gKeptUID = lResult['KeptUID'] end
                if lResult['PatientNameAnon'] then ldPatientNameAnon = lResult['PatientNameAnon'] end
                if lResult['PatientNameBase'] then gPatientNameBase  = lResult['PatientNameBase'] end
                if lResult['PatientNameIDChar'] then gPatientNameIDChar  = lResult['PatientNameIDChar'] end
                loStudyIDAnon = lResult['StudyIDAnon']
                if lResult['TopLevelTagToKeep'] then gTopLevelTagToKeep  = lResult['TopLevelTagToKeep'] end
                if lResult['UIDMap'] then gUIDMap = lResult['UIDMap'] end
            end

--             print('post anon -----------------------------------')
--             if gAddressConstructor then
--                 print('gAddressConstructor')
--                 print(DumpJson(gAddressConstructor))
--             end
--             if gAddressList then
--                 print('gAddressList')
--                 print(DumpJson(gAddressList))
--             end
--             if gKeptUID then
--                 print('gKeptUID')
--                 print(DumpJson(gKeptUID))
--             end
--             if ldPatientNameAnon then
--                 print('ldPatientNameAnon')
--                 print(ldPatientNameAnon)
--             end
--             if gPatientNameBase then
--                 print('gPatientNameBase')
--                 print(gPatientNameBase)
--             end
--             if gPatientNameIDChar then
--                 print('gPatientNameIDChar')
--                 print(gPatientNameIDChar)
--             end
--             if gTopLevelTagToKeep then
--                 print('gTopLevelTagToKeep')
--                 print(DumpJson(gTopLevelTagToKeep))
--             end
--             if gUIDMap then
--                 print('gUIDMap')
--                 print(DumpJson(gUIDMap))
--             end

            -- Set up old-->new UID map
            local lFlagRemapSOPInstanceUID = true
            local lFlagRemapKeptUID = true
            -- gUIDMap, gUIDType = MapUIDOldToNew(loStudyIDAnon,lFlagRemapSOPInstanceUID,lFlagRemapKeptUID)
            local lPostData = {}
            lPostData['StudyIDNew'] = loStudyIDAnon
            lPostData['FlagRemapSOPInstanceUID'] = lFlagRemapSOPInstanceUID
            lPostData['FlagRemapKeptUID'] = lFlagRemapKeptUID
            lPostData['KeptUID'] = gKeptUID
            local lResults = ParseJson(RestApiPost('/map_uid_old_to_new_lua', DumpJson(lPostData), false))
            gUIDMap = lResults['UIDMap']
            gUIDType = lResults['UIDType']
--             print('----------------map gen')
--             if gUIDMap then
--                 print('gUIDMap')
--                 print(DumpJson(gUIDMap))
--             end
--             if gUIDType then
--                 print('gUIDType')
--                 print(DumpJson(gUIDType))
--             end
            
            -- Set up replacements for AccessionNumber and StudyID
            local lReplaceRoot = {}
            lReplaceRoot['AccessionNumber'] = string.sub(loStudyIDAnon,1,8) .. string.sub(loStudyIDAnon,10,17)
            lReplaceRoot['StudyID'] = string.sub(loStudyIDAnon,19,26) .. string.sub(loStudyIDAnon,28,35)
    
            -- Check for existing lShiftEpoch
            -- local lShiftEpoch = LoadShiftEpochFromDB(lSQLpid)
            local lPostData = {}
            lPostData['SQLpid'] = lSQLpid
            local lStatus = ParseJson(RestApiPost('/load_shift_epoch_from_db_lua', DumpJson(lPostData), false))
            if lStatus['status'] and lStatus['status'] > 0 then error(lStatus['error_text']) end
            local lShiftEpoch = lStatus['ShiftEpoch']

            -- Compute lShiftEpoch
            if not lShiftEpoch then 
                -- Compute lShiftEpoch (used to shift earliest date to Jan 01 same year)
                -- lShiftEpoch = ComputeShiftEpochFromEarliestDate(loInstancesAnonMeta)
                -- Compute random shift up to one year
                math.randomseed(os.time())
                lShiftEpoch = math.floor(math.floor(math.random() * 365.0) * 24.0 * 3600.0)
                -- SaveShiftEpochToDB(lShiftEpoch,lSQLpid)
                local lPostData = {}
                lPostData['SQLpid'] = lSQLpid
                lPostData['ShiftEpoch'] = lShiftEpoch
                local lStatus = ParseJson(RestApiPost('/save_shift_epoch_to_db_lua', DumpJson(lPostData), false))
                if lStatus['status'] and lStatus['status'] > 0 then
                    error('Problem saving ShiftEpoch to DB')
                end
            end

            -- For some cases, we keep the dates, so lShiftEpoch=0
            local lFlagKeepOriginalDates = os.getenv('LUA_FLAG_KEEP_ORIGINAL_DATES') == 'true'
            if lFlagKeepOriginalDates then
                local currentTime = os.time
                lShiftEpoch = 0
            end

            -- Second pass anonymization creates files modified by lShiftEpoch
            -- Deletes First pass anonymized files following lShiftEpoch modification
            local lPostData = {}
            lPostData['InstancesMeta'] = loInstancesAnonMeta
            lPostData['ShiftEpoch'] = lShiftEpoch
            lPostData['ReplaceRoot'] = lReplaceRoot
            lPostData['UIDMap'] = gUIDMap
            lPostData['TopLevelTagToKeep'] = gTopLevelTagToKeep
            lPostData['AddressList'] = gAddressList
            lPostData['KeptUID'] = gKeptUID
            -- local loInstanceIDNew = ShiftDateTimePatAgeOfInstances(loInstancesAnonMeta, lShiftEpoch, lReplaceRoot)
            local lResults = ParseJson(RestApiPost('/shift_date_time_patage_of_instances_lua', DumpJson(lPostData), false))
            if lResults['status'] ~= 0 then
                error('Problem calling python shift date time patage')
            end
            loInstanceIDNew = lResults['InstanceIDNew']
    
            -- Delete the original instance
            for i, loInstanceAnonMeta in pairs(loInstancesAnonMeta) do
                loInstanceID = (loInstanceAnonMeta['ID'])
                RestApiDelete('/instances/' .. loInstanceID, false)
                --Delete(loInstanceID)
            end -- loop over loInstancesAnonMeta
    
            -- Send to receiving modality
            local lPostData = {}
            lPostData['orthanc_instance_ids'] = {}
            for i, loInstanceID in pairs(loInstanceIDNew) do
                table.insert(lPostData['orthanc_instance_ids'], loInstanceID)
            end
            local lResults = ParseJson(RestApiPost('/send_instances_to_remote_filter_lua', DumpJson(lPostData), false))
            if not lResults then
               error('Problem calling send_instances_to_remote_filter_lua')
            end 
            -- for i, loInstanceID in pairs(loInstanceIDNew) do
            for loInstanceID, lFlagSendToRemote in pairs(lResults) do
                -- local lFlagSendToRemote = SendToRemoteFilter(loInstanceID)
                if lFlagSendToRemote then
                    local dumby=3
                    if not lFlagForceAnon then
                        -- RestApiPost('/modalities/' .. os.getenv('LUA_ANON_ORTHANC') .. '/store', loInstanceID, false)
                        lFlagImagesSent = true
                    end
                else
                    RestApiDelete('/instances/' .. loInstanceID, false)
                    lFlagNonOriginalDetected = true
                end
            end

            if gVerbose then print(string.rep(' ',gIndent) .. 'Updating lookup table') end
            RestApiGet('/update_lookup_table_html_lua', false)
            -- UpdateLookupHTML()
            if ldPatientNameAnon then
                SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Anon Complete', 'Anonymization complete:' .. ldPatientNameAnon)
            else
                SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Anon Complete', 'Anonymization complete.')
            end

        else -- existing patient/study combo

           if gVerbose then print(string.rep(' ', gIndent) .. 'Skipping re-anon of existing patient/study') end

        end -- endif new patient or new study

        if lFlagNonOriginalDetected then
            if gVerbose then print('Some non-original images were not sent') end
        end

        -- CloseSQL()
        
    end -- endif no nonanonymized data detected

    if lFlagImagesSent and gVerbose then
        print(string.rep(' ',gIndent) .. 'Images sent to remote modalities') 
    end

    gIndent = gIndent - 3
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
    if gIndent > 0 then gIndent = gIndent - 3 end

end

-- -- ======================================================
-- function OnStableStudy(aoStudyID, aTags, aoStudyMeta)
-- 
--     gFlagForceAnon = false
--     gIndent = 0
--     local lFlagAnonymizeUponStable = os.getenv('LUA_FLAG_AUTO_ANON_WHEN_STABLE') == 'true'
--     if lFlagAnonymizeUponStable then
--        if (not aoStudyMeta['ModifiedFrom']) and (not aoStudyMeta['AnonymizedFrom']) and (not aoStudyMeta['ModifiedFrom']) then
--           SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Receipt', 'Stable subject received.  Anonymization proceeding.  Look for update upon success.')
--           OnStableStudyMain(aoStudyID, aTags, aoStudyMeta)
--        end
-- --     else
-- --        if (not aoStudyMeta['ModifiedFrom']) and (not aoStudyMeta['AnonymizedFrom']) and (not aoStudyMeta['AnonymizedFrom']) then
-- --           SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Receipt', 'Stable subject received.  You may wish to trigger a manual anonymization.')
-- --        end
--     end
-- 
-- end

-- -- ======================================================
-- -- Use of this seems limited to the Illumeo testing scenario.
-- -- Probably not necessary to convert this to python.
-- function ReAnonymizeStudy(aoStudyID)
-- 
--     gIndent=0
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Reanon ' .. aoStudyID) end
--     local lTime0 = os.time()
--     local loStudyMetadata = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
--     local lSIUID = loStudyMetadata['MainDicomTags']['StudyInstanceUID']
-- 
--     local lFlagSQLAlreadyOpen = gSQLOpen
--     if not lFlagSQLAlreadyOpen then OpenSQL() end
--     -- ConfirmLookupTablesSQL()
--     local lStatus = ParseJson(RestApiGet('/confirm_or_create_lookup_table_sql_lua', false, {['x-remote-user']='lua-ConfirmOrCreate'}))
--     if lStatus['error_text'] then
--         error(lStatus['error_text'])
--     end
-- 
--     local lSQLStatus, lSQLQuery, lSQLCursor, lSQLRow
--     -- Check for associated anonymized ID
--     lSQLQuery = string.format(
--                 [[SELECT value 
--                   FROM studyinstanceuid_anon
--                   WHERE siuid in (SELECT siuid
--                                   FROM studyinstanceuid
--                                   WHERE value='%s')]],
--                 gSQLConn:escape(lSIUID))
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying pid, parent_pid")
--     end
--     local lFlagReAnon = true
--     if lSQLCursor then
--         if lSQLCursor:numrows() > 0 then
--             lSQLRow = lSQLCursor:fetch({}, "a")
--             while lSQLRow do
--                 local loStudyIDAnon = ParseJson(RestApiPost('/tools/lookup', lSQLRow.value, false))
--                 if loStudyIDAnon then
--                     if #loStudyIDAnon > 0 then
--                         -- Check for existence of study on Orthanc
--                         if RestApiGet('/studies/' .. loStudyIDAnon[1]['ID'], false) then
--                             lFlagReAnon = false
--                         end
--                     end
--                 end
--                 lSQLRow = lSQLCursor:fetch({}, "a")
--             end
--         end
--     end
--     if not lFlagReAnon then
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Anon study exists on Orthanc.  Skipping.') end
--     else
--         gFlagForceAnon = true
--         SendEmailUpdate('IllumeoPhi Triggered Re-Anon', 'Manual re-anonymization triggered.  Look for update upon success.')
--         local tags = {} 
--         OnStableStudyMain(aoStudyID, tags, loStudyMetadata)           
--         gFlagForceAnon = false
--     end
--     if not lFlagSQLAlreadyOpen then CloseSQL() end
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     gIndent = nil
-- 
-- end
--    
-- -- ======================================================
-- Replaced with /jsanon link in python mod_rest_api.py
-- function AnonymizeStudy(aoStudyID)
-- 
--     gIndent=0
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     local lTime0 = os.time()
--     gFlagForceAnon = true
--     SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Triggered Anon', 'Manual anonymization triggered.  Look for update upon success.')
--     local tags = {} 
--     local loStudyMetadata = ParseJson(RestApiGet('/studies/' .. aoStudyID, false))
--     OnStableStudyMain(aoStudyID, tags, loStudyMetadata)           
--     gFlagForceAnon = false
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     -- SendEmailUpdate(os.getenv('ORTHANC__NAME') .. ' Anon Complete', 'AnonymizeStudy complete.')
--     gIndent = nil
-- 
-- end
-- 
-- -- ======================================================
-- function LoadPHI2AnonMap()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagSQLAlreadyOpen = gSQLOpen
--     if not lFlagSQLAlreadyOpen then OpenSQL() end
--     -- ConfirmLookupTablesSQL()
--     local lStatus = ParseJson(RestApiGet('/confirm_or_create_lookup_table_sql_lua', false, {['x-remote-user']='lua-ConfirmOrCreate'}))
--     if lStatus['error_text'] then
--         error(lStatus['error_text'])
--     end
-- 
--     local lPatientMap = {}
--     local lPatientReverseMap = {}
--     lPatientReverseMap['Primary'] = {}
--     lPatientReverseMap['Secondary'] = {}
--     lPatientReverseMap['Both'] = {}
-- 
--     local lSQLStatus, lSQLQuery, lSQLCursor, lSQLRow
-- 
--     -- Check for siuid2patientname_anon
--     lSQLQuery = [[SELECT table_name 
--                   FROM information_schema.tables 
--                   WHERE table_name='siuid2patientname_anon']]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     local lFlagSIUID2Anon
--     if not lSQLStatus then
--         lFlagSIUID2Anon = false
--     else
--         lFlagSIUID2Anon = true
--     end
-- 
--     -- Get PatientID 
--     lSQLQuery = [[SELECT pid,value 
--                   FROM patientid 
--                   WHERE parent_pid is NULL]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying pid, value")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             lPatientMap[lSQLRow.pid] = {}
--             lPatientMap[lSQLRow.pid]['PatientID'] = lSQLRow.value
--             lPatientMap[lSQLRow.pid]['OtherPatientIDs'] = {}
--             lPatientMap[lSQLRow.pid]['StudyInstanceUIDMap'] = {}
--             if lFlagSIUID2Anon then
--                 lPatientMap[lSQLRow.pid]['SIUID2NameAnonMap'] = {}
--             end
--             lPatientReverseMap['Primary'][lSQLRow.value] = lSQLRow.pid
--             lPatientReverseMap['Both'][lSQLRow.value] = lSQLRow.pid
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
--     lSQLQuery = [[SELECT parent_pid,value 
--                   FROM patientid 
--                   WHERE parent_pid is not NULL]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying pid, parent_pid")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             if lPatientMap[lSQLRow.parent_pid] then
--                 table.insert(lPatientMap[lSQLRow.parent_pid]['OtherPatientIDs'],
--                              lSQLRow.value)
--                 lPatientReverseMap['Secondary'][lSQLRow.value] = lSQLRow.parent_pid
--                 lPatientReverseMap['Both'][lSQLRow.value] = lSQLRow.parent_pid
--             end
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
-- 
--     lSQLQuery = [[SELECT value, pid 
--                   FROM patientid_anon]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying patientid_anon")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             if lPatientMap[lSQLRow.pid] then
--                 lPatientMap[lSQLRow.pid]['PatientIDAnon'] = lSQLRow.value
--             end
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
-- 
--     -- Get shift epoch
--     lSQLQuery = [[SELECT value, pid 
--                   FROM shiftepoch]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying shiftepoch")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             if lPatientMap[lSQLRow.pid] then
--                 lPatientMap[lSQLRow.pid]['ShiftEpoch'] = lSQLRow.value
--             end
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
-- 
--     -- Get internal number
--     lSQLQuery = [[SELECT value, pid FROM internalnumber]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying pid, parent_pid")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             if lPatientMap[lSQLRow.pid] then
--                 lPatientMap[lSQLRow.pid]['InternalNumber'] = lSQLRow.value
--             end
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
-- 
--     -- Gather study info
--     lSQLQuery = [[SELECT sphi.pid, sphi.value AS phivalue, sanon.value AS anonvalue  
--                   FROM studyinstanceuid sphi 
--                       INNER JOIN studyinstanceuid_anon sanon 
--                       ON sanon.siuid = sphi.siuid]]
--     lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--     if not lSQLStatus then 
--         CloseSQL()
--         error("Problem querying studyinstanceuid")
--     end
--     if lSQLCursor:numrows() > 0 then
--         lSQLRow = lSQLCursor:fetch({}, "a")
--         while lSQLRow do
--             if lPatientMap[lSQLRow.pid] then
--                 lPatientMap[lSQLRow.pid]['StudyInstanceUIDMap'][lSQLRow.phivalue] = lSQLRow.anonvalue
--             end
--             lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--         end
--     end
-- 
--     if lFlagSIUID2Anon then
-- 
--         -- Gather patientname_anon info
--         lSQLQuery = [[SELECT sphi.pid, sphi.value AS phivalue, sanon.patientname_anon AS anonvalue  
--                       FROM studyinstanceuid sphi 
--                           INNER JOIN siuid2patientname_anon sanon 
--                           ON sanon.siuid = sphi.siuid]]
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--         if not lSQLStatus then 
--             CloseSQL()
--             error("Problem querying studyinstanceuid")
--         end
--         if lSQLCursor:numrows() > 0 then
--             lSQLRow = lSQLCursor:fetch({}, "a")
--             while lSQLRow do
--                 if lPatientMap[lSQLRow.pid] then
--                     if not lPatientMap[lSQLRow.pid]['SIUID2NameAnonMap'][lSQLRow.phivalue] then
--                         lPatientMap[lSQLRow.pid]['SIUID2NameAnonMap'][lSQLRow.phivalue] = {}
--                     end
--                     lPatientMap[lSQLRow.pid]['SIUID2NameAnonMap'][lSQLRow.phivalue][lSQLRow.anonvalue] = true
--                 end
--                 lSQLRow = lSQLCursor:fetch(lSQLRow,"a")
--             end
--         end
-- 
--     end
-- 
--     if not lFlagSQLAlreadyOpen then CloseSQL() end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPatientMap, lPatientReverseMap, lFlagSIUID2Anon
-- 
-- end
-- 
-- -- ======================================================
-- function NowOnOrthanc()
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lFlagSQLAlreadyOpen = gSQLOpen
--     if not lFlagSQLAlreadyOpen then OpenSQL() end
--     -- ConfirmLookupTablesSQL()
--     local lStatus = ParseJson(RestApiGet('/confirm_or_create_lookup_table_sql_lua', false, {['x-remote-user']='lua-ConfirmOrCreate'}))
--     if lStatus['error_text'] then
--         error(lStatus['error_text'])
--     end
-- 
--     local lPatients = ParseJson(RestApiGet('/patients', false))
--     local lPatientIDModifier = ''
-- 
--     local lFlagSplitScreenFromDiagnostic = os.getenv('LUA_FLAG_SPLIT_SCREEN_DIAG') == 'true'
--     local lFlagEveryAccessionAPatient = os.getenv('LUA_FLAG_EVERY_ACCESSION_A_PATIENT') == 'true'
--     
--     local loSystemMeta = ParseJson(RestApiGet('/system', false))
-- 
--     local lNowOnOrthanc = {}
--     lNowOnOrthanc['ByPatientID'] = {}
--     lNowOnOrthanc['StudyInstanceUID2PatientID'] = {}
--     lNowOnOrthanc['PatientID2oPatientID'] = {}
--     lNowOnOrthanc['StudyUID2oStudyUID'] = {}
--     local lPatientIDTemp, lPatientID, lPatientIDModified
--     local lNumPatients = 0
--     for i, loPatientID in pairs(lPatients) do lNumPatients = lNumPatients+1 end
--     for i, loPatientID in pairs(lPatients) do
--         local lRowOfData = {}
--         -- local loPatientMeta = ParseJson(RestApiGet('/patients/' .. loPatientID .. '/shared-tags?simplify', false))
--         local loPatientMeta = ParseJson(RestApiGet('/patients/' .. loPatientID, false))
--         -- if gVerbose then print(string.rep(' ', gIndent+3) .. 'Orthanc patient query') end
--         -- local lPatientName = loPatientMeta['PatientName'] or ''
--         -- lPatientIDTemp = loPatientMeta['PatientID']
--         local lPatientName = loPatientMeta['MainDicomTags']['PatientName'] or ''
--         lPatientIDTemp = loPatientMeta['MainDicomTags']['PatientID']
--         lPatientID = lPatientIDTemp
--         -- Get PatientID from database
--         local lSQLStatus, lSQLQuery, lSQLCursor, lSQLRow
--         lSQLQuery = string.format(
--                 [[SELECT value FROM patientid WHERE pid IN (SELECT parent_pid FROM patientid WHERE value = '%s')]], 
--                 gSQLConn:escape(lPatientIDTemp))
--         lSQLStatus, lSQLCursor = pcall(gSQLConn.execute,gSQLConn,lSQLQuery)
--         if not lSQLStatus then 
--             CloseSQL()
--             error("Problem querying pid, value")
--         end
--         if lSQLCursor:numrows() > 0 then
--             lSQLRow = lSQLCursor:fetch({}, "a")
--             while lSQLRow do
--                 lPatientID = lSQLRow.value
--                 break
--             end
--         end
--         lRowOfData['PatientName'] = lPatientName
--         local loStudiesMeta = ParseJson(RestApiGet('/patients/' .. loPatientID .. '/studies', false))
--         lRowOfData['StudyDate'] = {}
--         lRowOfData['AccessionNumber'] = {}
--         lRowOfData['StudyInstanceUID'] = {}
--         local lAccessionNumber = {}
--         for j, loStudyMeta in pairs(loStudiesMeta) do
--             oStudyID = loStudyMeta['ID'] or ''
--             lPatientIDModifier = ''
--             if lFlagSplitScreenFromDiagnostic and (string.find(string.lower(lPatientName), string.lower(loSystemMeta['Name'])) == nil) then
--                 -- lPatientIDModifier = SetScreenOrDiagnostic(oStudyID)
--                 lPatientIDModifier = RestApiGet('/studies/' .. oStudyID .. '/set_screen_or_diagnostic', false)
--             end
--             if lFlagEveryAccessionAPatient and (string.find(string.lower(lPatientName), string.lower(loSystemMeta['Name'])) == nil) then 
--                 lPatientIDModifier = '_' .. loStudyMeta['MainDicomTags']['AccessionNumber']
--             end
--             lPatientIDModified = lPatientID .. lPatientIDModifier
--             lNowOnOrthanc['PatientID2oPatientID'][lPatientIDModified] = loPatientID
--             lRowOfData['StudyDate'][j] = loStudyMeta['MainDicomTags']['StudyDate'] or ''
--             lRowOfData['AccessionNumber'][j] = loStudyMeta['MainDicomTags']['AccessionNumber'] or ''
--             lRowOfData['StudyInstanceUID'][j] = loStudyMeta['MainDicomTags']['StudyInstanceUID']
--             lNowOnOrthanc['StudyInstanceUID2PatientID'][lRowOfData['StudyInstanceUID'][j]] = lPatientIDModified
--             lNowOnOrthanc['StudyUID2oStudyUID'][lRowOfData['StudyInstanceUID'][j]] = oStudyID
--         end
--         lNowOnOrthanc['ByPatientID'][lPatientIDModified] = lRowOfData
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lNowOnOrthanc
-- 
-- end
-- 
-- -- ======================================================
-- function LoadLookupTable(aFileLookup,aMakeBackup)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Loading lookup table') end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--  
--     local lLun = io.open(aFileLookup,"r")
--     if not lLun then
--         return nil
--     end
--    
--     local lLun = assert(io.open(aFileLookup,"r"))
--     local lFileData = lLun:read("*all")
--     lLun:close()
-- 
--     if aMakeBackup then
--         local lOut = assert(io.open(aFileLookup .. "." .. os.date("%Y%m%d%H%M%S"),"w"))
--         lOut:write(lFileData)
--         lOut:close()
--     end
--      
--     local lDataTHead = string.match(lFileData, "<table.*<thead>.*<tr>(.*)</tr>.*</thead>")
--     local lLookupTable = {}
--     local lDataKeys = {}
--     local lIndexCol = 1
--     for lHeader in string.gmatch(lDataTHead, "<th>([^<]*)</th>") do
--         lDataKeys[lIndexCol] = lHeader
--         lIndexCol = lIndexCol + 1
--         lLookupTable[lHeader] = {}
--     end
--     local lDataTBody = string.match(lFileData, "<tbody>(.*)</tbody>")
--     local lIndexRow = 1
--     for lRow in string.gmatch(lDataTBody, "<tr>(.-)</tr>") do
--         local lIndexCol = 1
--         for lCol in string.gmatch(lRow, "<td[^>]*>[\r\n]*(.-)[\r\n]*</td>") do
--             local lColumnStripped = string.match(lCol, "<a [^>]*>[\r\n]*([^<]*)</a>")
--             if not lColumnStripped then
--                 lColumnStripped = lCol
--             end
--             local lEntry = nil
--             if string.match(lColumnStripped,",") then
--                 local lIndexEntry = 1
--                 lEntry = {}
--                 local lSingleEntry
--                 for lSingleEntry in string.gmatch(lColumnStripped, "([^,]*)[,%s]*") do
--                     if string.match(lSingleEntry,"[^%s]+") then
--                         lEntry[lIndexEntry] = lSingleEntry
--                         lIndexEntry = lIndexEntry + 1
--                     end
--                 end
--                 if lIndexEntry < 2 then
--                     lEntry = nil
--                 end
--             else
--                 if string.len(trim(lColumnStripped)) > 0 then
--                     lEntry = lColumnStripped
--                 end
--             end
--             if lEntry then
--                 lLookupTable[lDataKeys[lIndexCol]][lIndexRow] = lEntry
--             else
--                 lLookupTable[lDataKeys[lIndexCol]][lIndexRow] = 'BLANK'
--             end
--             lIndexCol = lIndexCol + 1
--         end
--         lIndexRow = lIndexRow + 1
--     end
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
--     return lLookupTable
--     
-- end
-- 
-- -- ======================================================
-- function LoadLookupTableFast(aFileLookup, aMakeBackup)
-- 
--     -- I'm going to hard code the lookup location just in case someone gets the idea to escape the execute statement and wreak havoc
--     local lFileLookup = "/media/html/lookup/master/lookuptable.html"
--     local lTempFile = os.tmpname()
--     -- local lCommand = "sed 's/&nbsp//g' " .. aFileLookup .. " | html2text -nobs -width 2048 | grep \"|\" | sed 's/_//g'" .. " > " .. lTempFile
--     local lCommand = "sed 's/&nbsp//g' " .. lFileLookup .. " | html2text -nobs -width 2048 | grep \"|\" | sed 's/_/ /g'" .. " > " .. lTempFile
--     local lResult = os.execute(lCommand)
--     if lResult == 1 then
--         return nil
--     end
-- 
--     local lLun = io.open(lTempFile,"r")
--     if lLun == nil then
--         return nil
--     end
--     lLun:close()
-- 
--     local lLun = io.open(lFileLookup,"r")
--     if lLun == nil then
--         return nil
--     end
--     lLun:close()
-- 
--     if aMakeBackup then
--         -- local lLun = assert(io.open(aFileLookup,"r"))
--         local lLun = assert(io.open(lFileLookup,"r"))
--         local lFileData = lLun:read("*all")
--         lLun:close()
--         -- local lOut = assert(io.open(aFileLookup .. "." .. os.date("%Y%m%d%H%M%S"),"w"))
--         local lOut = assert(io.open(lFileLookup .. "." .. os.date("%Y%m%d%H%M%S"),"w"))
--         lOut:write(lFileData)
--         lOut:close()
--     end
-- 
--     local lLines = {}
--     for lLine in io.lines(lTempFile) do
--         lLines[#lLines + 1] = lLine
--     end
--     if not os.remove(lTempFile) then
--        return nil
--     end
-- 
--     local lLookupTable = {}
--     local lDataKeys = {}
--     local lIndexCol = 1
--     for lHeader in string.gmatch(string.sub(lLines[1],2,-1),"([^|]*)|") do
--         lDataKeys[lIndexCol] = trim(lHeader)
--         lIndexCol = lIndexCol + 1
--         lLookupTable[trim(lHeader)] = {}
--     end
-- 
--     local lIndexRow = 1
--     for i = 2, #lLines do
--         local lRow = string.sub(lLines[i],2,-1)
--         local lIndexCol = 1
--         for lColumnStripped in string.gmatch(lRow, "([^|]*)|") do
--             local lEntry = nil
--             if string.match(trim(lColumnStripped),",") then
--                 local lIndexEntry = 1
--                 lEntry = {}
--                 local lSingleEntry
--                 for lSingleEntry in string.gmatch(trim(lColumnStripped), "([^,]*)[,%s]*") do
--                     if string.match(lSingleEntry,"[^%s]+") then
--                         lEntry[lIndexEntry] = lSingleEntry
--                         lIndexEntry = lIndexEntry + 1
--                     end
--                 end
--                 if lIndexEntry < 2 then
--                     lEntry = nil
--                 end
--             else
--                 if string.len(trim(lColumnStripped)) > 0 then
--                     lEntry = trim(lColumnStripped)
--                 end
--             end
--             if lEntry then
--                 lLookupTable[lDataKeys[lIndexCol]][lIndexRow] = lEntry
--             else
--                 lLookupTable[lDataKeys[lIndexCol]][lIndexRow] = 'BLANK'
--             end
--             lIndexCol = lIndexCol + 1
--         end
--         lIndexRow = lIndexRow + 1
--     end
-- 
--     return lLookupTable
-- 
-- end
-- 
-- -- ======================================================
-- function FindPACSInLookupTableFromSIUID(aLookupTable,aStudyInstanceUID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     gIndent = gIndent + 3
--     -- if gVerbose then print(string.rep(' ', gIndent) .. 'Scanning existing lookup table') end
--     local lRow, lFound
--     for lRowTemp, lStudyInstanceUIDs in pairs(aLookupTable['StudyInstanceUID']) do 
--         lFound = false
--         lRow = lRowTemp
--         if type(lStudyInstanceUIDs) == 'table' then
--             for lCol, lStudyInstanceUID in ipairs(lStudyInstanceUIDs) do
--                 lFound = lStudyInstanceUID == aStudyInstanceUID
--                 if lFound then break end
--             end
--         else
--             lFound = lStudyInstanceUIDs == aStudyInstanceUID
--         end
--         if lFound then break end
--     end
--     gIndent = gIndent - 3
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     if not lFound then return nil,nil end
-- 
--     local lPACSData = nil
--     if aLookupTable['Name'][lRow] then
--         local lPatientName = nil
--         if type(aLookupTable['Name'][lRow]) == 'table' then
--             lPatientName = table.concat(aLookupTable['Name'][lRow],',')
--         else
--             lPatientName = aLookupTable['Name'][lRow]
--         end
--         if lPatientName and (lPatientName ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0010,0010'] = {}
--             lPACSData['0010,0010']['Value'] = lPatientName
--         end
--     end
--     if aLookupTable['PatientID'][lRow] then
--         local lPatientID = nil
--         if type(aLookupTable['PatientID'][lRow]) == 'table' then
--             lPatientID = table.concat(aLookupTable['PatientID'][lRow],',')
--         else
--             lPatientID = aLookupTable['PatientID'][lRow]
--         end
--         if lPatientID and (lPatientID ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0010,0020'] = {}
--             lPACSData['0010,0020']['Value'] = lPatientID
--         end
--     end
--     if aLookupTable['Date'][lRow] then
--         local lStudyDate = nil
--         if type(aLookupTable['Date'][lRow]) == 'table' then
--             lStudyDate = table.concat(aLookupTable['Date'][lRow],',')
--         else
--             lStudyDate = aLookupTable['Date'][lRow]
--         end
--         if lStudyDate and (lStudyDate ~= 'BLANK') then
--             local lAnonDate = nil
--             if aLookupTable['Anon Date'] then
--                 if type(aLookupTable['Anon Date'][lRow]) == 'table' then
--                     lAnonDate = table.concat(aLookupTable['Anon Date'][lRow],',')
--                 else
--                     lAnonDate = aLookupTable['Anon Date'][lRow]
--                 end
--             else
--                 lAnonDate = 'BLANK'
--             end
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0008,0020'] = {}
--             lPACSData['0008,0020']['Value'] = lStudyDate
--             if lAnonDate and (lAnonDate ~= 'BLANK') then
--                 lPACSData['AnonDate'] = lAnonDate
--             end
--         end
--     end
--     if aLookupTable['Accession'][lRow] then
--         local lAccession = nil
--         if type(aLookupTable['Accession'][lRow]) == 'table' then
--             lAccession = table.concat(aLookupTable['Accession'][lRow],',')
--         else
--             lAccession = aLookupTable['Accession'][lRow]
--         end
--         if lAccession and (lAccession ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0008,0050'] = {}
--             lPACSData['0008,0050']['Value'] = lAccession
--         end
--     end
-- 
--     if not lPACSData then
--         lFound = nil
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Subject not in lookup table') end
--     else
--         lFound = true
--         -- if gVerbose then print(string.rep(' ', gIndent) .. 'Subject in lookup table') end
--     end
--     gIndent = gIndent - 3
--     if gIndent > 0 then gIndent = gIndent - 3 end
--  
--     return lPACSData, lFound 
-- 
-- end
-- 
-- -- ======================================================
-- function FindPACSInLookupTableFromPatientID(aLookupTable,aPatientID)
-- 
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     gIndent = gIndent + 3
--     -- if gVerbose then print(string.rep(' ', gIndent) .. 'Scanning existing lookup table') end
--     local lRow, lFound
--     for lRowTemp, lPatientIDs in pairs(aLookupTable['PatientID']) do 
--         lFound = false
--         lRow = lRowTemp
--         if type(lPatientIDs) == 'table' then
--             for lCol, lPatientID in ipairs(lPatientIDs) do
--                 lFound = lPatientID == aPatientID
--                 if lFound then break end
--             end
--         else
--             lFound = lPatientIDs == aPatientID
--         end
--         if lFound then break end
--     end
-- 
--     gIndent = gIndent - 3
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     if not lFound then return nil,nil end
-- 
--     local lPACSData = nil
--     if aLookupTable['Name'][lRow] then
--         local lPatientName = nil
--         if type(aLookupTable['Name'][lRow]) == 'table' then
--             lPatientName = table.concat(aLookupTable['Name'][lRow],',')
--         else
--             lPatientName = aLookupTable['Name'][lRow]
--         end
--         if lPatientName and (lPatientName ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0010,0010'] = {}
--             lPACSData['0010,0010']['Value'] = lPatientName
--         end
--     end
--     if aLookupTable['PatientID'][lRow] then
--         local lPatientID = nil
--         if type(aLookupTable['PatientID'][lRow]) == 'table' then
--             lPatientID = table.concat(aLookupTable['PatientID'][lRow],',')
--         else
--             lPatientID = aLookupTable['PatientID'][lRow]
--         end
--         if lPatientID and (lPatientID ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0010,0020'] = {}
--             lPACSData['0010,0020']['Value'] = lPatientID
--         end
--     end
--     if aLookupTable['Date'][lRow] then
--         local lStudyDate = nil
--         if type(aLookupTable['Date'][lRow]) == 'table' then
--             lStudyDate = table.concat(aLookupTable['Date'][lRow],',')
--         else
--             lStudyDate = aLookupTable['Date'][lRow]
--         end
--         if lStudyDate and (lStudyDate ~= 'BLANK') then
--             local lAnonDate = nil
--             if aLookupTable['Anon Date'] then
--                 if type(aLookupTable['Anon Date'][lRow]) == 'table' then
--                     lAnonDate = table.concat(aLookupTable['Anon Date'][lRow],',')
--                 else
--                     lAnonDate = aLookupTable['Anon Date'][lRow]
--                 end
--             else
--                 lAnonDate = 'BLANK'
--             end
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0008,0020'] = {}
--             lPACSData['0008,0020']['Value'] = lStudyDate
--             if lAnonDate and (lAnonDate ~= 'BLANK') then
--                 lPACSData['AnonDate'] = lAnonDate
--             end
--         end
--     end
--     if aLookupTable['Accession'][lRow] then
--         local lAccession = nil
--         if type(aLookupTable['Accession'][lRow]) == 'table' then
--             lAccession = table.concat(aLookupTable['Accession'][lRow],',')
--         else
--             lAccession = aLookupTable['Accession'][lRow]
--         end
--         if lAccession and (lAccession ~= 'BLANK') then
--             if not lPACSData then lPACSData = {} end
--             lPACSData['0008,0050'] = {}
--             lPACSData['0008,0050']['Value'] = lAccession
--         end
--     end
-- 
--     if not lPACSData then
--         lFound = nil
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Subject not in lookup table') end
--     else
--         lFound = true
--         if gVerbose then print(string.rep(' ', gIndent) .. 'Subject in lookup table') end
--     end
--  
--     gIndent = gIndent - 3
--     if gIndent > 0 then gIndent = gIndent - 3 end
--     return lPACSData, lFound 
-- 
-- end
-- 
-- -- ======================================================
-- function UpdateLookupHTML()
-- 
--     local lFlagKeepOriginalDates = os.getenv('LUA_FLAG_KEEP_ORIGINAL_DATES') == 'true'
--     if gIndent then gIndent=gIndent+3 else gIndent=0 end
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
--     gIndent = gIndent + 3
--     local lTime0 = os.time()
--     local lPatientMap, lPatientReverseMap, lFlagSIUID2Anon
--     lPatientMap, lPatientReverseMap, lFlagSIUID2Anon = LoadPHI2AnonMap()
--     local lNowOnOrthanc = NowOnOrthanc()
-- 
--     -- Check for the main modality that could be queried
--     local lFlagXRefModality=false
--     local lXRefModality=nil
--     if os.getenv('LUA_XREF_MODALITY') then
--         for _, lModality in pairs(ParseJson(RestApiGet('/modalities', false))) do
--             if lModality == os.getenv('LUA_XREF_MODALITY') then
--                 lFlagXRefModality = true
--                 lXRefModality = lModality
--                 break
--             end
--         end  
--     end
--     if lFlagXRefModality then
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'FlagXRefModality=1') end
--     else
--         if gVerbose then print(string.rep(' ', gIndent+3) .. 'FlagXRefModality=1') end
--     end
-- 
--     -- Check for existing lookup table
--     local lFileLookup = "/media/html/lookup/master/lookuptable.html"
--     local lBackup = true
--     -- local lLookupTable = LoadLookupTable(lFileLookup,lBackup)
--     local lLookupTable = LoadLookupTableFast(lFileLookup,lBackup)
-- 
--     -- Prepare to output the new
--     file_out = io.open(lFileLookup, "w")
--     io.output(file_out)
-- 
--     io.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-us">\n')
--     io.write('<head>\n')
--     io.write('<link rel="stylesheet" href="style.css" type="text/css" id="" media="print, projection, screen" />\n')
--     io.write('<link rel="stylesheet" href="theme.blue.min.css">\n')
--     io.write('<script type="text/javascript" src="../../../app/libs/jquery.min.js"></script>\n')
--     io.write('<script type="text/javascript" src="jquery.tablesorter.combined.min.js"></script>\n')
--     io.write('<script type="text/javascript">\n')
--     io.write('$(document).ready(function() { \n')
--     io.write('    // call the tablesorter plugin \n')
--     io.write('    $("table").tablesorter({\n')
--     io.write('        theme: "blue",\n')
--     io.write('        widgets: ["zebra", "filter"],\n')
--     io.write('        widgetOptions : {\n')
--     io.write('            filter_columnFilters: true,\n')
--     io.write('            filter_reset: ".reset",\n')
--     io.write('            zebra : [ "normal-row", "alt-row" ]\n')
--     io.write('        },\n')
--     io.write('        sortList : [[2,0]]\n')
--     io.write('    }); \n')
--     io.write('}); \n')
--     io.write('</script>\n')
--     io.write('</head>\n')
--     
--     io.write('<body>\n')
--     io.write('<a href="../../../app/explorer.html">Return to Orthanc home page</a></br>')
--     io.write('Click a column heading to sort.</br>')
--     io.write('Click <a href="updatelookup.html">here</a> to force an update of this table.</br>\n')
--     io.write('<!-- targeted by the "filter_reset" option -->\n')
--     io.write('<button type="button" class="reset">Reset Search</button>\n')
--     io.write('<table class="tablesorter-blue" border=1>\n')
--     io.write('<thead>\n')
--     io.write('<tr>\n')
--     io.write('<th>Name</th>\n')
--     io.write('<th>PatientID</th>\n')
--     io.write('<th>ID</th>\n')
--     if lFlagSIUID2Anon then
--         io.write('<th>Name Anon</th>\n')
--     end
--     io.write('<th>Date</th>\n')
--     io.write('<th>Anon Date</th>\n')
--     io.write('<th>Accession</th>\n')
--     io.write('<th>Alt PatientID</th>\n')
--     io.write('<th>Anon PatientID</th>\n')
--     io.write('<th>StudyInstanceUID</th>\n')
--     io.write('<th>Anon StudyInstanceUID</th>\n')
--     io.write('</tr>\n')
--     io.write('</thead>\n')
--     io.write('<tbody>\n')
--     local lPatientIDShort, lPostData, lPostResult
--     for lPatientID, lPID in pairs(lPatientReverseMap['Primary']) do
-- 
--         local lShiftEpoch
--         if lFlagKeepOriginalDates then
--            lShiftEpoch = 0
--         else 
--            lShiftEpoch = lPatientMap[lPID]['ShiftEpoch']
--         end
--         if string.sub(lPatientID, -3) == 'n2d' then
--             lPatientIDShort = string.sub(lPatientID,1,string.find(lPatientID,'n2d')-1)
--         elseif string.sub(lPatientID, -2) == '2d' then
--             lPatientIDShort = string.sub(lPatientID,1,string.find(lPatientID,'2d')-1)
--         else
--             lPatientIDShort = lPatientID
--         end
-- 
--         local lStudyInstanceUIDPrinted = {}
--         if lNowOnOrthanc['ByPatientID'][lPatientID] then
-- 
--             -- if gVerbose then print(string.rep(' ', gIndent) .. 'Now on orthanc: ' .. lPID) end
--             for j, lDate in pairs(lNowOnOrthanc['ByPatientID'][lPatientID]['StudyDate']) do 
--                 lStudyInstanceUIDPrinted[lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]] = true
--                 io.write('<tr>\n')
--                 io.write('<td>\n')
--                 io.write('<a href="../../../app/explorer.html#patient?uuid=' .. lNowOnOrthanc['PatientID2oPatientID'][lPatientID] .. '">\n')
--                 io.write(lNowOnOrthanc['ByPatientID'][lPatientID]['PatientName'])
--                 io.write('</a>\n')
--                 io.write('</td>\n')
--                 io.write('<td align="right">' .. lPatientIDShort .. '</td>\n')
--                 io.write('<td align="right">\n')
--                 if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                     io.write('<a href="../../../app/explorer.html#patient?uuid=' .. lNowOnOrthanc['PatientID2oPatientID'][lPatientMap[lPID]['PatientIDAnon']] .. '">\n')
--                 end
--                 io.write(lPatientMap[lPID]['InternalNumber'])
--                 if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                     io.write('</a>\n')
--                 end
--                 io.write('</td>\n')
--                 if lFlagSIUID2Anon then
--                     if lPatientMap[lPID]['SIUID2NameAnonMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID']] then
--                         io.write('<td>\n')
--                         for k, _ in pairs(lPatientMap[lPID]['SIUID2NameAnonMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID']]) do
--                             io.write(k .. ', ')
--                         end
--                         io.write('</td>\n')
--                     else
--                         io.write('<td>&nbsp</td>\n')
--                     end
--                 end
--                 io.write('<td align="center">' .. lDate .. '</td>\n')
--                 if lFlagKeepOriginalDates or not lShiftEpoch then
--                     if lFlagKeepOriginalDates then
--                         io.write('<td align="center">' .. lDate .. '</td>\n')
--                     else
--                         io.write('<td align="center">&nbsp</td>\n')
--                     end
--                 else
--                     -- local lNewDateString = hiftDateTimeString(lShiftEpoch, lDate)
--                     local lPostData = {}
--                     lPostData['ShiftEpoch'] = lShiftEpoch
--                     lPostData['YYYYMMDD'] = lDate
--                     local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--                     local lNewDateString = lResults['NewDateString']
--                     io.write('<td align="center">' .. lNewDateString .. '</td>\n')
--                 end
--                 io.write('<td align="right">' .. lNowOnOrthanc['ByPatientID'][lPatientID]['AccessionNumber'][j] .. '</td>\n')
--                 io.write('<td>\n')
--                 for k, lAltPID in pairs(lPatientMap[lPID]['OtherPatientIDs']) do 
--                     io.write(lAltPID .. ', \n')
--                 end
--                 io.write('</td>\n')
--                 io.write('<td align="center">\n')
--                 if lPatientMap[lPID]['PatientIDAnon'] then
--                     if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                         io.write('<a href="../../../app/explorer.html#patient?uuid=' .. lNowOnOrthanc['PatientID2oPatientID'][lPatientMap[lPID]['PatientIDAnon']] .. '">\n')
--                     end
--                     io.write(lPatientMap[lPID]['PatientIDAnon'])
--                     if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                         io.write('</a>\n')
--                     end
--                 else
--                     io.write('&nbsp')
--                 end
--                 io.write('</td>\n')
--                 io.write('<td align="right">\n')
--                 io.write('<a href="../../../app/explorer.html#study?uuid=' .. lNowOnOrthanc['StudyUID2oStudyUID'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]] .. '">\n')
--                 io.write(lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j])
--                 io.write('</a>\n')
--                 io.write('</td>\n')
--                 io.write('<td align="right">\n')
--                 if lNowOnOrthanc['StudyUID2oStudyUID'][lPatientMap[lPID]['StudyInstanceUIDMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]]] then
--                     io.write('<a href="../../../app/explorer.html#study?uuid=' .. lNowOnOrthanc['StudyUID2oStudyUID'][lPatientMap[lPID]['StudyInstanceUIDMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]]] .. '">\n')
--                 end
--                 if lPatientMap[lPID]['StudyInstanceUIDMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]] then
--                     io.write(lPatientMap[lPID]['StudyInstanceUIDMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]])
--                 else
--                     io.write('')
--                 end
--                 if lNowOnOrthanc['StudyUID2oStudyUID'][lPatientMap[lPID]['StudyInstanceUIDMap'][lNowOnOrthanc['ByPatientID'][lPatientID]['StudyInstanceUID'][j]]] then
--                     io.write('</a>\n')
--                 end
--                 io.write('</td>\n')
--                 io.write('</tr>\n')
--             end
--         end
--         for lStudyInstanceUID, lStudyInstanceUIDAnon in pairs(lPatientMap[lPID]['StudyInstanceUIDMap']) do
--             -- if gVerbose then print(string.rep(' ', gIndent) .. 'With studies: ' .. lPID) end
--             if not lStudyInstanceUIDPrinted[lStudyInstanceUID] then
--                 local lPACSData = nil
--                 local lLookupMatch = false
--                 if lLookupTable then
--                     lPACSData, lLookupMatch = FindPACSInLookupTableFromSIUID(lLookupTable,lStudyInstanceUID)
--                     if not lPACSData then
--                         if gVerbose then print('Not found in lookup: ' .. lStudyInstanceUID) end
--                     end
--                 end
--                 if lFlagXRefModality and (not lPACSData) and (not string.match(lPatientMap[lPID]['PatientID'], '[^0-9]')) then
--                     local lPatientIDList = {}
--                     table.insert(lPatientIDList, lPatientMap[lPID]['PatientID'])
--                     if next(lPatientMap[lPID]['OtherPatientIDs']) then
--                         local lOtherPatientID
--                         for _, lOtherPatientID in pairs(lPatientMap[lPID]['OtherPatientIDs']) do
--                             if not string.match(lOtherPatientID, '[^0-9]') then
--                                 table.insert(lPatientIDList, lOtherPatientID)
--                             end
--                         end
--                     end
--                     for _, lOtherPatientID in pairs(lPatientIDList) do 
--                         lPostData = {}
--                         lPostData['Level'] = 'Study'
--                         lPostData['Query'] = {}
--                         lPostData['Query']['StudyInstanceUID'] = lStudyInstanceUID
--                         lPostData['Query']['PatientID'] = lOtherPatientID
--                         lPostResult = ParseJson(RestApiPost('/modalities/' .. lXRefModality .. '/query', DumpJson(lPostData,true), false))
--                         if lPostResult['ID'] then
--                             local lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'], false))
--                             if lQuery[1] == "answers" then
--                                 lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers', false))
--                                 if lQuery[1] == "0" then
--                                     lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0', false))
--                                     if lQuery[1] == "content" then
--                                         lPACSData = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0/content', false))
--                                         if lPACSData then
--                                             break
--                                         end
--                                     end
--                                 end
--                             end
--                         end
--                     end
--                     if not lPACSData then
--                         for _, lOtherPatientID in pairs(lPatientIDList) do 
--                             lPostData = {}
--                             lPostData['Level'] = 'Patient'
--                             lPostData['Query'] = {}
--                             lPostData['Query']['PatientID'] = lOtherPatientID
--                             lPostResult = ParseJson(RestApiPost('/modalities/' .. lXRefModality .. '/query', DumpJson(lPostData,true), false))
--                             if lPostResult['ID'] then
--                                 local lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'], false))
--                                 if lQuery[1] == "answers" then
--                                     lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers', false))
--                                     if lQuery[1] == "0" then
--                                         lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0', false))
--                                         if lQuery[1] == "content" then
--                                             lPACSData = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0/content', false))
--                                             if lPACSData then
--                                                 break
--                                             end
--                                         end
--                                     end
--                                 end
--                             end
--                         end
--                     end
--                 end
--                 io.write('<tr>\n')
--                 if lPACSData then
--                     if lPACSData['0010,0010'] then
--                         io.write('<td>' .. lPACSData['0010,0010']['Value'] .. '</td>\n')
--                     else
--                         io.write('<td>&nbsp</td>\n')
--                     end
--                 else
--                     io.write('<td>&nbsp</td>\n')
--                 end
--                 if lPACSData then
--                     if lPACSData['0010,0020'] then
--                         io.write('<td>' .. lPACSData['0010,0020']['Value'] .. '</td>\n')
--                     else
--                         io.write('<td>&nbsp</td>\n')
--                     end
--                 else
--                     io.write('<td align="right">' .. lPatientIDShort .. '</td>\n')
--                 end
--                 io.write('<td align="right">\n')
--                 if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                     io.write('<a href="../../../app/explorer.html#patient?uuid=' .. lNowOnOrthanc['PatientID2oPatientID'][lPatientMap[lPID]['PatientIDAnon']] .. '">\n')
--                 end
--                 if lPatientMap[lPID]['InternalNumber'] then
--                     io.write(lPatientMap[lPID]['InternalNumber'])
--                 else
--                     io.write('')
--                 end
--                 if lNowOnOrthanc['ByPatientID'][lPatientMap[lPID]['PatientIDAnon']] then
--                     io.write('</a>\n')
--                 end
--                 io.write('</td>\n')
--                 if lFlagSIUID2Anon then
--                     if lPatientMap[lPID]['SIUID2NameAnonMap'][lStudyInstanceUID] then
--                         io.write('<td>\n')
--                         for k, _ in pairs(lPatientMap[lPID]['SIUID2NameAnonMap'][lStudyInstanceUID]) do
--                             io.write(k .. ', ')
--                         end
--                         io.write('</td>\n')
--                     else
--                         io.write('<td>&nbsp</td>\n')
--                     end
--                 end
--                 if lPACSData then
--                     if lPACSData['0008,0020'] then
--                         io.write('<td>' .. lPACSData['0008,0020']['Value'] .. '</td>\n')
--                         if lFlagKeepOriginalDates or not lShiftEpoch then
--                             if lFlagKeepOriginalDates then
--                                 io.write('<td>' .. lPACSData['0008,0020']['Value'] .. '</td>\n')
--                             else
--                                 io.write('<td>&nbsp</td>\n')
--                             end
--                         else
--                             local lNewDateString
--                             if (not lLookupMatch) or (lLookupTable and (not lPACSData['AnonDate']) and (lPACSData['0008,0020']['Value'] ~= 'NotInPACS')) then
--                                 -- lNewDateString = ShiftDateTimeString(lShiftEpoch,lPACSData['0008,0020']['Value'])
--                                 local lPostData = {}
--                                 lPostData['ShiftEpoch'] = lShiftEpoch
--                                 lPostData['YYYYMMDD'] = lPACSData['0008,0020']['Value']
--                                 local lResults = ParseJson(RestApiPost('/shift_date_time_string_lua', DumpJson(lPostData,true), false))
--                                 lNewDateString = lResults['NewDateString']
--                             else
--                                 lNewDateString = lPACSData['AnonDate'] or 'BLANK'
--                             end
--                             io.write('<td>' .. lNewDateString .. '</td>\n')
--                         end
--                     else
--                         io.write('<td>NotInPACS</td>\n')
--                         io.write('<td>&nbsp</td>\n')
--                     end
--                 else
--                     io.write('<td>NotInPACS</td>\n')
--                     io.write('<td>&nbsp</td>\n')
--                 end
--                 if lPACSData then
--                     if lPACSData['0008,0050'] then
--                         io.write('<td>' .. lPACSData['0008,0050']['Value'] .. '</td>\n')
--                     else
--                         io.write('<td>NotInPACS</td>\n')
--                     end
--                 else
--                     io.write('<td>NotInPACS</td>\n')
--                 end
--                 io.write('<td>\n')
--                 for k, lAltPID in pairs(lPatientMap[lPID]['OtherPatientIDs']) do 
--                     io.write(lAltPID .. ', \n')
--                 end
--                 if lPACSData then
--                     if lPACSData['0010,0020'] then
--                         if lPACSData['0010,0020']['Value'] ~= lPatientIDShort then
--                             io.write(lPatientIDShort)
--                         end
--                     end
--                 end
--                 io.write('</td>\n')
--                 if lPatientMap[lPID]['PatientIDAnon'] then
--                     io.write('<td align="center">' .. lPatientMap[lPID]['PatientIDAnon'] .. '</td>\n')
--                 else
--                     io.write('<td align="center">&nbsp</td>\n')
--                 end
--                 io.write('<td align="right">' .. lStudyInstanceUID .. '</td>\n')
--                 io.write('<td align="right">\n')
--                 if lNowOnOrthanc['StudyUID2oStudyUID'][lStudyInstanceUIDAnon] then
--                     io.write('<a href="../../../app/explorer.html#study?uuid=' .. lNowOnOrthanc['StudyUID2oStudyUID'][lStudyInstanceUIDAnon] .. '">\n')
--                 end
--                 io.write(lStudyInstanceUIDAnon)
--                 if lNowOnOrthanc['StudyUID2oStudyUID'][lStudyInstanceUIDAnon] then
--                     io.write('</a>\n')
--                 end
--                 io.write('</td>\n')
--                 io.write('</tr>\n')
--             end
--         end
--         io.flush()
--     end
--     io.write('</tbody>\n')
--     io.write('</table>\n')
--     io.write('</body>\n')
--     io.write('</html>\n')
--     io.close(file_out)
-- 
--     gIndent = gIndent - 3
--     if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
--     if gIndent > 0 then gIndent = gIndent - 3 end
-- 
-- end
-- 
-- -- ========================================
-- function IncomingHttpRequestFilter(method, uri, ip, username, httpHeaders)
-- 
--     local lRemoteUser = httpHeaders['x-remote-user']
--     local lRemoteAddr = httpHeaders['x-forwarded-for']
-- 
--     lI, lJ = string.find(uri, 'images')
--     if lI == nil then
--         PrintRecursive(lRemoteUser .. ' ' .. lRemoteAddr .. ' ' .. method .. ' ' .. uri)
--     end
-- 
--     -- gVerbose = lRemoteUser == os.getenv('LUA_X_REMOTE_USER_ALLOWED_TO_TRIGGER')
--     local lAllowedToTrigger = SplitToKeyList(os.getenv('LUA_X_REMOTE_USER_ALLOWED_TO_TRIGGER'), ".")
--     gVerbose = lAllowedToTrigger[lRemoteUser]
-- 
--     if string.find(uri, '/extra/lookup/master/updatelookup.html') then
--         UpdateLookupHTML()
--     end
-- 
--     local lAnonymize = string.find(uri, '/anonymize')
--     if lAnonymize then
--         if lAllowedToTrigger[lRemoteUser] then
--             loStudyID = string.match(uri, "/studies/([0-9a-f%-]+)/anonymize")
--             if loStudyID then
--                 if gVerbose then print('Anonymize ' .. loStudyID) end
--                 AnonymizeStudy(loStudyID)
--             end
--         end
--         return false
--     end
-- 
--     local lLuaExecute = string.find(uri, '/execute-script')
--     if lLuaExecute and not lAllowedToTrigger[lRemoteUser] then
--         return false
--     end
-- 
--     return true
-- 
-- end
-- 
-- ========================================
function OutgoingFindRequestFilter(query, modality)
    for key, value in pairs(query) do
       if value == '*' then
          query[key] = ''
       end
    end
    return query

end

-- ========================================
function SendEmailUpdate(aSubject, aMessage)

    if gIndent then gIndent=gIndent+3 else gIndent=0 end
    if gVerbose then print(string.rep(' ', gIndent) .. 'Entering ' .. debug.getinfo(1,"n").name) end
    gIndent = gIndent + 3
    local lTime0 = os.time()
    local lFlagSendEmailUpdate = os.getenv('LUA_MAIL_AUTO') == 'true'
    if lFlagSendEmailUpdate then

        local lDataToPython = {}
        lDataToPython['Subject'] = aSubject
        lDataToPython['Message'] = aMessage
        local lPostEmail = ParseJson(RestApiPost('/email_message_lua', DumpJson(lDataToPython,true), false, {['x-remote-user']='lua-SendEmailUpdate'}))
        if lPostEmail['error_text'] then
            if gVerbose then print(string.rep(' ', gIndent+3) .. 'Error sending mail ' .. lPostEmail['error_text']) end
        end
        
--         local lMailTo = os.getenv('LUA_MAIL_TO'):gsub("^['\"]*(.-)['\"]*$", "%1")
--  
--         smtp = require("socket.smtp")
--         from = os.getenv('ORTHANC__NAME') .. ' <' .. os.getenv('ORTHANC__NAME') .. '@' .. os.getenv('LUA_MAIL_ORIGIN') .. '>'
--         rcpt = {lMailTo}
--         
--         mesgt = {
--            headers = {
--               to = lMailTo, 
--               subject = aSubject
--            },
--            body = aMessage
--         }
--         
--         r, e = smtp.send{
--            server = os.getenv('LUA_MAIL_SERVER'), 
--            from = from, 
--            rcpt = rcpt, 
--            source = smtp.message(mesgt)
--         }
--         if e then
--            print(r)
--            print(e)
--         end
 
    end
 
    gIndent = gIndent - 3
    if gVerbose then print(string.rep(' ', gIndent) .. 'Time spent in ' .. debug.getinfo(1,"n").name .. ': ', os.time()-lTime0) end
    if gIndent > 0 then gIndent = gIndent - 3 end

end

-- -- ========================================
-- function PrepareDataForAnonymizeGUI(aQueryPACS)
-- 
--     local lQueryPACS = false
--     if aQueryPACS then lQueryPACS = aQueryPACS end
--     
--     local lVerbose = gVerbose
--     gVerbose = nil
--     local lDataForAnonymizeGUI = {}
--     local lStudyDate = {}
--     lDataForAnonymizeGUI['StudyMeta'] = {}
--     lDataForAnonymizeGUI['SeriesMeta'] = {}
--     lDataForAnonymizeGUI['DB'] = {}
--     lDataForAnonymizeGUI['PACS'] = {}
--     lDataForAnonymizeGUI['Lookup'] = {}
--     -- Cross reference modality
--     local lFlagXRefModality=false
--     local lXRefModality=nil
--     if os.getenv('LUA_XREF_MODALITY') then
--         for _, lModality in pairs(ParseJson(RestApiGet('/modalities', false))) do
--             if lModality == os.getenv('LUA_XREF_MODALITY') then
--                 lXRefModality = lModality
--                 lFlagXRefModality = true
--                 break
--             end
--         end  
--     end
--     
--     -- Check for existing lookup table
--     local lFileLookup = "/media/html/lookup/master/lookuptable.html"
--     local lBackup = false
--     -- local lLookupTable = LoadLookupTable(lFileLookup,lBackup)
--     local lLookupTable = LoadLookupTableFast(lFileLookup,lBackup)
-- 
--     -- Data in the database
--     local lPatientMap, lPatientReverseMap, lFlagSIUID2Anon
--     lPatientMap, lPatientReverseMap, lFlagSIUID2Anon = LoadPHI2AnonMap()
-- 
--     -- DICOM now on Orthanc
--     for ioStudyID, oStudyID in pairs(ParseJson(RestApiGet('/studies', false))) do
--         local lFlagFirstImage = true
--         local lStudyMeta = ParseJson(RestApiGet('/studies/' .. oStudyID, false))
--         local lPatientIDModifier = ''
--         local lStudyInstanceUIDModifier = ''
--         if not (lStudyMeta['AnonymizedFrom'] or lStudyMeta['ModifiedFrom']) then
-- 
--             local lStudyInstanceUID = lStudyMeta['MainDicomTags']['StudyInstanceUID'] .. lStudyInstanceUIDModifier
--             local lPatientID = lStudyMeta['PatientMainDicomTags']['PatientID'] .. lPatientIDModifier
--             local lOtherPatientIDs
--             if lStudyMeta['PatientMainDicomTags']['OtherPatientIDs'] then
--                 lOtherPatientIDs = lStudyMeta['PatientMainDicomTags']['OtherPatientIDs'] .. lPatientIDModifier
--             else
--                if lStudyMeta['PatientMainDicomTags']['RETIRED_OtherPatientIDs'] then
--                    lOtherPatientIDs = lStudyMeta['PatientMainDicomTags']['RETIRED_OtherPatientIDs'] .. lPatientIDModifier
--                end
--             end
--             
--             -- Store the study meta
--             lDataForAnonymizeGUI['StudyMeta'][oStudyID] = lStudyMeta
--             lStudyDate[oStudyID] = lStudyMeta['MainDicomTags']['StudyDate'] .. 'T' .. 
--                                    lStudyMeta['MainDicomTags']['StudyTime']
-- 
--             -- Check the lookup table
--             if lLookupTable then
--                 lDataForAnonymizeGUI['Lookup'][oStudyID] = {}
--                 lDataForAnonymizeGUI['Lookup'][oStudyID]['Found'] = 0
--                 local lPACSData = nil
--                 local lLookupMatch = false
--                 lPACSData, lLookupMatch = FindPACSInLookupTableFromSIUID(lLookupTable,lStudyInstanceUID)
--                 if not iLookupMatch then
--                     if gVerbose then print('Not found in lookup: ' .. lStudyInstanceUID) end
--                     lPACSData, lLookupMatch = FindPACSInLookupTableFromPatientID(lLookupTable,lPatientID)
--                     if not lPACSData then
--                         if gVerbose then print('Not found in lookup (patid): ' .. lPatientID) end
--                     end
--                 end
--                 if lPACSData then
--                     lDataForAnonymizeGUI['Lookup'][oStudyID]['Found'] = 1
--                     lDataForAnonymizeGUI['Lookup'][oStudyID]['Data'] = {}
--                     for lName, lAddress in pairs({PatientName='0010,0010',PatientID='0010,0020',StudyDate='0008,0020',AccessionNumber='0008,0050',PatientBirthDate='0010,0030'}) do 
--                         if lPACSData[lAddress] then
--                             lDataForAnonymizeGUI['Lookup'][oStudyID]['Data'][lName] =  lPACSData[lAddress]['Value']
--                         end
--                     end
--                 end
--             end
-- 
--             -- Check PACS
--             if lFlagXRefModality and lQueryPACS then
--                 lDataForAnonymizeGUI['PACS'][oStudyID] = {}
--                 lDataForAnonymizeGUI['PACS'][oStudyID]['Found'] = 0
--                 local lPACSData = nil
--                 local lPostData = {}
--                 lPostData['Level'] = 'Study'
--                 lPostData['Query'] = {}
--                 lPostData['Query']['StudyInstanceUID'] = lStudyInstanceUID
--                 lPostData['Query']['PatientID'] = lPatientID
--                 lPostResult = ParseJson(RestApiPost('/modalities/' .. lXRefModality .. '/query', DumpJson(lPostData,true), false))
--                 if lPostResult['ID'] then
--                     local lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'], false))
--                     if lQuery[1] == "answers" then
--                         lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers', false))
--                         if lQuery[1] == "0" then
--                             lQuery = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0', false))
--                             if lQuery[1] == "content" then
--                                 lPACSData = ParseJson(RestApiGet('/queries/' .. lPostResult['ID'] .. '/answers/0/content', false))
--                             end
--                         end
--                     end
--                 end
--                 if lPACSData then
--                     lDataForAnonymizeGUI['PACS'][oStudyID]['Found'] = 1
--                     lDataForAnonymizeGUI['PACS'][oStudyID]['Data'] = {}
--                     for lName, lAddress in pairs({PatientName='0010,0010',PatientID='0010,0020',StudyDate='0008,0020',AccessionNumber='0008,0050',PatientBirthDate='0010,0030'}) do 
--                         if lPACSData[lAddress] then
--                             lDataForAnonymizeGUI['PACS'][oStudyID]['Data'][lName] =  lPACSData[lAddress]['Value']
--                         end
--                     end
--                 end
--             end
-- 
--             if lFlagFirstImage then
-- 
--                 -- Store the DB matches
--                 local lDB = {}
--                 -- local lPatientIDs, lFlagNewPatientID, lSQLpidUnique, ldPatientIDAnon
--                 -- lPatientIDs, lFlagNewPatientID, lSQLpidUnique, ldPatientIDAnon = CheckDBForExistingPatientIDs(lStudyMeta,lPatientIDModifier)
--                 local lPID = lPatientReverseMap['Both'][lPatientID]
--                 if lPID then
--                     lDB['FoundPatientID'] = 1
--                 else
--                     if lOtherPatientIDs then
--                         lPID = lPatientReverseMap['Both'][lOtherPatientIDs]
--                     end
--                     if lPID then
--                         lDB['FoundPatientID'] = 2
--                     end
--                 end
--                 lDB['FoundStudyInstanceUID'] = 0
--                 lDB['FoundOtherStudyInstanceUID'] = 0
--                 if lPID then
--                     lDB['pid'] = lPID
--                     lDB['InternalNumber'] = lPatientMap[lPID]['InternalNumber']
--                     if lPatientMap[lPID]['StudyInstanceUIDMap'] then
--                         for lOtherStudyInstanceUID,lAnonStudyInstanceUID in pairs(lPatientMap[lPID]['StudyInstanceUIDMap']) do
--                             if (lOtherStudyInstanceUID ~= lStudyInstanceUID) then
--                                 if lDB['OtherStudyInstanceUID'] then
--                                     lDB['OtherStudyInstanceUID'] = lDB['OtherStudyInstanceUID'] .. ', ' .. lOtherStudyInstanceUID
--                                 else
--                                     lDB['OtherStudyInstanceUID'] = lOtherStudyInstanceUID
--                                 end
--                                 lDB['FoundOtherStudyInstanceUID'] = 1
--                             end
--                         end 
--                     end
--                     if lFlagSIUID2Anon and lPatientMap[lPID]['SIUID2NameAnonMap'] then
--                         if lPatientMap[lPID]['SIUID2NameAnonMap'][lStudyInstanceUID] then
--                             lDB['FoundStudyInstanceUID'] = 1
--                             lDB['FoundNameAnon'] = 1
--                             for lNameAnon, lStatus in pairs(lPatientMap[lPID]['SIUID2NameAnonMap'][lStudyInstanceUID]) do
--                                 if lDB['NameAnon'] then
--                                     lDB['NameAnon'] = lDB['NameAnon'] .. ', ' .. lNameAnon
--                                 else
--                                     lDB['NameAnon'] = lNameAnon
--                                 end
--                             end
--                         else
--                             lDB['FoundNameAnon'] = 0
--                         end
--                     else
--                         lDB['FoundNameAnon'] = 0
--                     end
--                     -- local ldStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon, lFlagNewStudyInstanceUID
--                     -- ldStudyInstanceUID, lFlagNewStudyInstanceUID, lSQLsiuid, ldStudyInstanceUIDAnon = CheckDBForExistingStudyInstanceUIDs(lStudyMeta,lDB['pid'],lStudyInstanceUIDModifier)
--                 else
--                     lDB['FoundPatientID'] = 0
--                 end
--                 lDataForAnonymizeGUI['DB'][oStudyID] = lDB
-- 
--                 -- Store the Series Meta
--                 for ioSeriesID, oSeriesID in pairs(lStudyMeta['Series']) do
--                     local lSeriesMeta = ParseJson(RestApiGet('/series/' .. oSeriesID, false))
--                     if lSeriesMeta['Instances'] then
--                         lFlagFirstImage = false
--                         local lSeriesMetaTable = {}
--                         lSeriesMetaTable['Manufacturer'] = lSeriesMeta['Manufacturer']
--                         lSeriesMetaTable['Modality'] = lSeriesMeta['Modality']
--                         lSeriesMetaTable['StationName'] = lSeriesMeta['StationName']
--                         for ioInstanceID, oInstanceID in pairs(lSeriesMeta['Instances']) do
--                             local lInstanceMeta = ParseJson(RestApiGet('/instances/' .. oInstanceID .. '/simplified-tags', false))
--                             if lInstanceMeta then
--                                 lSeriesMetaTable['InstitutionAddress'] = lInstanceMeta['InstitutionAddress'] or 'Unknown InstitutionAddress'
--                                 lSeriesMetaTable['InstitutionName'] = lInstanceMeta['InstitutionName'] or 'Unknown InstitutionName'
--                                 lSeriesMetaTable['PatientAge'] = lInstanceMeta['PatientAge'] or 'Unknown PatientAge'
--                                 lSeriesMetaTable['OtherPatientNames'] = lInstanceMeta['OtherPatientNames'] or 'Unknown OtherPatientNames'
--                                 lSeriesMetaTable['Modality'] = lInstanceMeta['Modality'] or 'Unknown Modality'
--                                 lSeriesMetaTable['IssuerOfPatientID'] = lInstanceMeta['IssuerOfPatientID'] or 'Unknown IssuerOfPatientID'
--                                 break
--                             end
--                         end
--                         lDataForAnonymizeGUI['SeriesMeta'][oStudyID] = lSeriesMetaTable
--                     end
--                     if not lFlagFirstImage then break end
--                 end
--         
--                 -- Erase the Series data since the GUI doesn't need it
--                 -- Because structures are copied by reference, doing so here erases what's 
--                 -- already stored in the GUI data structure
--                 lStudyMeta['Series'] = ''
-- 
--             end
--         end
--     end
--     table.sort(lStudyDate,function(a,b) return a>b end)
--     lDataForAnonymizeGUI['StudyDate'] = lStudyDate
-- 
--     print(DumpJson(lDataForAnonymizeGUI,true))
--     gVerbose = lVerbose
-- 
-- end
-- 
