$(document).ready(function(){

  $('.dropdown').on('click', function(){
    $('#notice-link').on('mouseenter', function(){
      $('#notification_active').on('click', function(){
        var id = $(this).attr('data-id')
        $.ajax({
          type: 'POST',
          url: '{% url "blog:mark_notification_as_read" %}',
          data: {'id': id, 'csrfmiddlewaretoken': '{{csrf_token}}'},
          dataType: 'json',
          success: function(response){
            console.id(slug);
          },
          error: function(rs, e){
            console.log(rs.responseText);
          }
        });
      })
    })
  })
  function mark_all_as_read(){
    $('#close_all').on('click', function(){
      $.ajax({
        type: 'POST',
        url: '{% url "blog:mark_all_notifications_as_read" %}',
        data: {'session_key': '{{request.session.session_key|escapejs}}', 'csrfmiddlewaretoken': '{{csrf_token|escapejs}}'},
        dataType: 'json',
        success: function(response)
        {
          console.log(response)
          $('.live_notify_badge').text(0)
        },
        error: function(rs, e){
          console.log(rs.responseText);
        }
      });
    })
  }
})
