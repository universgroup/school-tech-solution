       
    //    const cycleDataBox = document.getElementById('')       
    //    $.ajax({
    //         type : 'GET',
    //         url : '/listecycle/',
    //         success : function(response){
    //             console.log(response.data) 
    //             const cycleData = response.data
    //             cycleData.map(item=>{
    //                 const option = document.createElement('div')
    //                 option.textContent = item.name
    //                 option.setAttribute('class', 'form-control')
    //                 option.setAttribute('data-value', item.name)

    //             })
    //         },
    //         error: function(error){
    //         console.log(error)
    //         }
    //     })

    // $("#id_idcycle").change(function(){
    //     const url = $("#finscription").attr("data-classe-url");
    //     const idcycle = $(this).val();

    //     $.ajax({
    //         url:url,
    //         data:{
    //             'idcycle':idcycle
    //         },
    //         success:function(data){
    //             $("#id_idclasse").html(data);
    //         }


    //     });
    // });


		$(document).ready(function()
		{
			var $select1 = $('#select1'),
					$select2 = $('#select2'),
					$options = $select2.find('option');
					$select1.on('change',function()
					{
						$select2.html($options.filter('[value="' + this.value + '"]'));
					}).trigger('change');
		});

    $(document).ready(function()
    {
        $('#select1').$select2({

        });

        $('#select2').$select2({

        });
        
    });


