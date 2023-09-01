var gui_data;
var current_oid;
var stop_prog;

function updateAnonName() {
    if (gui_data == null) {return;}
    var base = $( "#ase_entry_base" ).val();
    if (gui_data.DB[current_oid].FoundPatientID > 0) {
       $("#ase_current_name").text(base + '^ID' + '0'.repeat(6-gui_data.DB[current_oid].InternalNumber.length) + gui_data.DB[current_oid].InternalNumber + '^^^');
    } else {
       $("#ase_current_name").text(base + '^ID######^^^');
    } 
}

function showProg() {
  stop_prog = 0;
  var div_pbar = document.getElementById("div_pbar");   
  var width = 1;
  var id_prog = setInterval(frame, 10);
  $( '#div_progress' ).show();
  function frame() {
     if (stop_prog == 1) {
        clearInterval(id_prog);
        $( '#div_progress' ).hide();
     }
     width++; 
     width = width % 100;
     div_pbar.style.width = width + '%'; 
  }
}

function fillPACSTable(member,id_table) {

    $(id_table + ' tbody').remove();
    if (member in gui_data) {
        if (current_oid in gui_data[member]) {
            var $pacs_table = $(id_table);
            if (gui_data[member][current_oid].Found == 1) {
                $.each(gui_data[member][current_oid].Data, function( index, value ) {
                    $pacs_table.append($('<tr />').val(index).html(
                            '<th align="left">' + index + '</th><td>' + value + '</td>'));
                    });
            }
        }
    }
}

function fillDBTable() {
    var $db_table = $('#ase_table_db');
    $('#ase_table_db tbody').remove(); 
    if (gui_data.DB[current_oid].FoundPatientID > 0) {
        $db_table.append($('<tr />').val('dbfound').html(
                '<th align="left">' + 'Matched PatientID' + '</th><td bgcolor="lightgreen">' + 'Yes' + '</td>'));
        $db_table.append($('<tr />').val('internalnumber').html(
                '<th align="left">' + 'Internal Number' + '</th><td>' + gui_data.DB[current_oid].InternalNumber + '</td>'));
    }
    if (gui_data.DB[current_oid].FoundStudyInstanceUID > 0) {
        $db_table.append($('<tr />').val('siuidfound').html(
                '<th align="left">' + 'Matched StudyInstanceUID' + '</th><td bgcolor="lightgreen">' + 'Yes' + '</td>'));
    }
    if (gui_data.DB[current_oid].FoundOtherStudyInstanceUID > 0) {
        $db_table.append($('<tr />').val('siuidotherfound').html(
                '<th align="left">' + 'Other Studies Found' + '</th><td>' + gui_data.DB[current_oid].OtherStudyInstanceUID + '</td>'));
    }
    if (gui_data.DB[current_oid].FoundNameAnon > 0) {
        $db_table.append($('<tr />').val('nameanon').html(
                '<th align="left">' + 'Anonymized Names' + '</th><td>' + gui_data.DB[current_oid].NameAnon + '</td>'));
    }
}

function fillStudyTable() {

    var $study_table = $('#ase_table_study');
    $('#ase_table_study tbody').remove(); 
    $.each(gui_data.StudyMeta[current_oid].PatientMainDicomTags, function( index, value ) {
           var color_string = '';
           if ((gui_data.DB[current_oid].FoundPatientID > 0) && ((index == 'PatientID') || (index == 'RETIRED_OtherPatientIDs'))) {
               if (gui_data.DB[current_oid].FoundPatientID == 1) {
                   if (index == 'PatientID') {
                       color_string = ' bgcolor="lightgreen"';
                   } else {
                       color_string = ' bgcolor="yellow"';
                   }
               } else {
                   if (index == 'PatientID') {
                       color_string = ' bgcolor="yellow"';
                   } else {
                       color_string = ' bgcolor="lightgreen"';
                   }
               }
           }
           $study_table.append($('<tr />').val(index).html(
               '<th align="left">' + index + '</th><td' + color_string + '>' + value + '</td>'));
           });
    $.each(gui_data.StudyMeta[current_oid].MainDicomTags, function( index, value ) {
           var color_string = '';
           if (index == 'StudyInstanceUID') {
               if (gui_data.DB[current_oid].FoundStudyInstanceUID == 1) {
                   color_string = ' bgcolor="lightgreen"';
               } else {
                   if (gui_data.DB[current_oid].FoundOtherStudyInstanceUID == 1) {
                       color_string = ' bgcolor="yellow"';
                   } else {
                       color_string = ' bgcolor="pink"';
                   }
               }
           }
           $study_table.append($('<tr />').val(index).html(
               '<th align="left">' + index + '</th><td' + color_string + '>' + value + '</td>'));
           });
    $.each(gui_data.SeriesMeta[current_oid], function( index, value ) {
            $study_table.append($('<tr />').val(index).html(
                    '<th align="left">' + index + '</th><td>' + value + '</td>'));
            });
}

$( window ).on( 'load', function() {
    showProg();
    $("#ase_status_col").css("background-color", "white");
    $.get('../../system', 
        function( result ){
            if ( result != null) {
                var $ase_select_base=$('#ase_select_base');
                $ase_select_base.append($('<option />').val(result.Name).text('Orthanc Default'));
            } 
        });
/*
    $.post('../../tools/execute-script', 
        {data: 'PrepareDataForAnonymizeGUI()'}, 
*/
    $.get('../../prepare_data_for_anonymize?pacs=0', 
        function(resultJSON,status){
            if (status == 'success') {
                if (resultJSON != null) {
                    var $study_select=$('#ase_select_study');
                    //gui_data = $.parseJSON(resultJSON);
                    gui_data = resultJSON;
                    $.each(gui_data.StudyDate, function( index, value ) {
                        $study_select.append($('<option />').val(index).text(
                                'Date: ' + value + ' ' + 
                                'Acc: ' + gui_data.StudyMeta[index].MainDicomTags.AccessionNumber + ' ' + 
                                'SID: ' + gui_data.StudyMeta[index].MainDicomTags.StudyID + ' ' + 
                                'Name: ' + gui_data.StudyMeta[index].PatientMainDicomTags.PatientName));
                    });
                    current_oid = $( '#ase_select_study' ).val();
                    fillStudyTable();
                    fillDBTable();
                    fillPACSTable('PACS','#ase_table_pacs');
                    fillPACSTable('Lookup','#ase_table_lu');
                    stop_prog = 1;
                }
            }
        }
    );
});

$( window ).on( 'load', function() {
    $( '#ase_select_study' ).change( function() {
        current_oid = $( '#ase_select_study' ).val();
        fillStudyTable();
        fillDBTable();
        fillPACSTable('PACS','#ase_table_pacs');
        fillPACSTable('Lookup','#ase_table_lu');
        updateAnonName();
    });
});

$( window ).on( 'load', function() {
    $( '#button_pacs' ).click( function() {
        showProg();
/*
        $.post('../../tools/execute-script', 
            {data: 'PrepareDataForAnonymizeGUI(true)'}, 
*/
    $.get('../../prepare_data_for_anonymize?pacs=1', 
            function(resultJSON,status){
                if (status == 'success') {
                    if (resultJSON != null) {
                        var $study_select=$('#ase_select_study');
                        //gui_data = $.parseJSON(resultJSON);
                        gui_data = resultJSON;
                        $study_select.empty();
                        $.each(gui_data.StudyDate, function( index, value ) {
                            $study_select.append($('<option />').val(index).text(
                                    'Date: ' + value + ' ' + 
                                    'Acc: ' + gui_data.StudyMeta[index].MainDicomTags.AccessionNumber + ' ' + 
                                    'Name: ' + gui_data.StudyMeta[index].PatientMainDicomTags.PatientName));
                        });
                        current_oid = $( '#ase_select_study' ).val();
                        fillStudyTable();
                        fillDBTable();
                        fillPACSTable('PACS','#ase_table_pacs');
                        fillPACSTable('Lookup','#ase_table_lu');
                        stop_prog = 1;
                    }
                }
            }
        );
    });
});

$( window ).on( 'load', function() {
   $( '#ase_button_base' ).click( function() {
      $("#ase_status_col").css("background-color", "white");
      var value_patient_basename = $( "#ase_entry_base" ).val();
      var reject_characters = /[^a-zA-Z0-9_]/g;
      if (reject_characters.test(value_patient_basename)) {
         alert('Only [a-zA-Z0-9_] characters permitted');
      } else {
         if (value_patient_basename == "") {
            $.get("../../get_patient_name_base", 
                   function(result,status){
                      $("#ase_status_base").html('Yes');
                      if (status == "success") {
                         $("#ase_status_col").css("background-color", "lightgreen");
                         if (result != null) {
                            $( "#ase_entry_base" ).val(result.PatientNameBase);
                            $("#ase_current_base").text(result.PatientNameBase);
                            updateAnonName();
                         }
                      } else {
                         $("#ase_status_col").css("background-color", "pink");
                      }
                   }
                  );
         } else {
            var request = $.ajax({
                url:'../../set_patient_name_base', 
                type: 'POST',
                contentType: 'application/json', 
                data: "{\"PatientNameBase\" : \"" + value_patient_basename + "\"}",
                dataType: "json",
                success : function( msg ) {
                   $("#ase_status_col").css("background-color", "lightgreen");
                   $("#ase_status_base").html('Yes');
                   $("#ase_current_base").text(value_patient_basename);
                   updateAnonName();
                },
                error: function( jqXHR, text_status ) {
                   $("#ase_status_col").css("background-color", "pink");
                   alert(JSON.stringify(jqXHR));
                   alert( "Request failed: " + text_status );
                }
            });
         }
      }
   });
});

$( document ).ready(function() {
   $( "#ase_select_base" ).change( function() {
      $( "#ase_entry_base" ).val(this.value);
      $("#ase_status_col").css("background-color", "yellow");
      $("#ase_status_base").html('No');
      updateAnonName();
   });
});

$( document ).ready(function() {
   //$( "#ase_entry_base" ).val($( "#ase_select_base").val());
   $( "#ase_entry_base" ).val();
   $("#ase_button_base").trigger( "click" );
});

$( document ).ready(function() {
   $("#ase_entry_base").on('keyup', function (e) {
       if (e.keyCode == 13) {
          $("#ase_button_base").trigger( "click" );
       }
   });
});

$( window ).on( 'load', function() {
   $( '#ase_initiate_anon' ).click( function() {
      var current_name = $( '#ase_current_name' ).text();
      var patient_study = $( '#ase_select_study option:selected').text();
      var proceed = confirm('To Be Anonymized\n\n' + patient_study + '\n\nWith Basename (ie. IRB): ' + current_name + '\n\nProceed?');
      if (proceed == false) {
         return;
      } 
      showProg();
/*      $.post("../../tools/execute-script", 
             {data : "AnonymizeStudy('" + current_oid + "')"}, */
      $.post("../../studies/" + current_oid + "/jsanon", 
             {data : ""},
             function(result,status){
                stop_prog = 1;
                if (status == "success") {
                   alert('Success!');
                   location.reload();
                } else {
                   alert("Problem with anon: " + status);
                }
             }
         );
     });
});

